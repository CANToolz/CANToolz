"""

Module to support CAN hardware over serial implementing LAWICEL protocol.

Example of supported setup:
    - Seeed CAN-BUS Shield (http://wiki.seeed.cc/CAN-BUS_Shield_V1.2/)
    - Arduino flashed with firmware implementing CAN232 protocol (https://github.com/latonita/arduino-canbus-monitor)

"""

import serial
import struct
import binascii

from cantoolz import can232
from cantoolz.can import CANMessage
from cantoolz.module import CANModule, Command


class hw_CAN232(CANModule):

    """Module to support CAN hardware over serial implementing LAWICEL protocol."""

    name = 'CAN232 Serial LAWICEL'
    help = """

    This module supports CAN hardware that communicates over serial using CAN232/CANUSB protocol (a.k.a LAWICEL).

    Init parameters example:

        - 'port': 'COM3'          # Serial port or path
        - 'serial_speed': 115200  # Serial connection speed (default: 115200)
        - 'speed': '250KBPS'      # CAN Bus speed (default: '500KBPS')
        - 'debug': 1              # Debug level (default: 0)

    Module parameters:

        - 'action': 'read'        # Action to perform ('read' or 'write')
        - 'pipe': 2               # Pipe to read from/write to (default: 1)

    """
    version = 0.1
    id = 7
    _bus = 'CAN232'

    _COM_port_name = None
    _COM_port = None
    _COM_speed = None
    _COM_delay = 0.1
    _CAN_speed = None
    _C232 = None

    def do_init(self, params):
        """Initialize the serial communication with the CAN hardware."""
        self.DEBUG = int(params.get('debug', 0))
        self.dprint(1, 'Initializating hardware starting...')

        self._COM_port_name = params.get('port', None)
        if not self._COM_port_name:
            raise ValueError('No port specified (e.g. COM3, /dev/ttyACM0)')
        self._COM_speed = params.get('serial_speed', 115200)
        self._CAN_speed = params.get('speed', '500KBPS')
        self.init_port()

        self.dprint(1, 'C232 version: {0}'.format(self._C232.version(max_tries=100)))

        self._cmdList['V'] = Command('Get version number of the CANBUS hardware', 0, '', self.cmd_version, True)
        self._cmdList['N'] = Command('Get serial number of the CANBUS hardware', 0, '', self.cmd_serial, True)
        self._cmdList['O'] = Command('Open communication channel with the CANBUS hardware', 0, '', self.cmd_open, True)
        self._cmdList['L'] = Command('Open communication channel in read only with the CANBUS hardware', 0, '', self.cmd_ropen, True)
        self._cmdList['C'] = Command('Close communication channel with the CANBUS hardware', 0, '', self.cmd_close, True)
        self._cmdList['Speed'] = Command('Set speed of CAN bus (e.g. 500KBPS)', 1, '<speed>', self.cmd_speed, True)
        self._cmdList['F'] = Command('Get status flag from the CANBUS hardware', 0, '', self.cmd_status, True)
        self._cmdList['Z'] = Command('Switch on/off the timestamp on the CAN frames', 1, '<True/False>', self.cmd_timestamp, True)
        self._cmdList['t'] = Command('Transmit a standard (11bit) frame (format iiiLDD..DD; e.g. 10021133)', 1, '<cmd>', self.cmd_transmit_std, True)
        self._cmdList['T'] = Command('Transmit an extended (29bit) frame (format iiiiiiiiLDD..DD; e.g. 0000010021133)', 1, '<cmd>', self.cmd_transmit_ext, True)
        self._cmdList['r'] = Command('Transmit a remote standard (11bit) frame (format iiiL; e.g. 1002)', 1, '<cmd>', self.cmd_transmit_rtr_std, True)
        self._cmdList['R'] = Command('Transmit a remote extended (29bit) frame (format iiiiiiiiL; e.g. 000001002)', 1, '<cmd>', self.cmd_transmit_rtr_ext, True)
        return 0

    def init_port(self):
        """Initialize the serial communication with the hardware device."""
        if self._COM_port_name is 'loop':  # Useful for debugging without hardware but not perfect.
            self._COM_port = serial.serial_for_url('loop://', timeout=0.5)
        else:
            self._COM_port = serial.Serial(self._COM_port_name, baudrate=self._COM_speed, timeout=0.5)
        self._C232 = can232.CAN232(self._COM_port, speed=self._CAN_speed, delay=self._COM_delay, debug=self.DEBUG)

    def get_status(self, def_in):
        return 'Current status: {0}\nSpeed: {1}\nPort: {2}'.format(self._active, self._COM_speed, self._COM_port_name)

    def do_start(self, params):
        """Start the LAWICEL communication."""
        self.dprint(1, 'Opening LAWICEL channel')
        self._C232.open()
        if not self._C232.opened:
            return -1
        return 0

    def do_stop(self, params):
        """Stop the LAWICEL communication."""
        self.dprint(1, 'Closing LAWICEL channel')
        self._C232.close()
        if self._C232.opened:
            return -1
        return 0

    def do_exit(self, params):
        """Exit the module."""
        self._COM_port.close()
        return 0

    def do_read(self, can, params):
        """Read from the hardware."""
        frame = b''
        while not frame:
            frame = self._C232.read_frame()
            if not frame or not self._C232.is_valid_frame(frame):
                continue
            can.bus = self._bus
            self.dprint(1, 'New frame: {0} (hex: {1})'.format(frame, self.get_hex(frame)))
            if frame.startswith((can232.CMD_TRANSMIT_STD, can232.CMD_TRANSMIT_RTR_STD)):  # 11bit CAN frame
                id = struct.unpack('!H', binascii.unhexlify(frame[1:4].zfill(4)))[0]
                length = int(frame[4:5], 16)
                if frame.startswith(can232.CMD_TRANSMIT_STD):  # RTR frames don't have data
                    # TODO: Handle timestamp in frame if timestamp enabled..
                    data = list(binascii.unhexlify(frame[5:]))
                    type = CANMessage.DataFrame
                else:
                    # TODO: Handle timestamp in frame if timestamp enabled..
                    type = CANMessage.RemoteFrame
                can.CANFrame = CANMessage(id, length, data, False, type)
                can.CANData = True
            elif frame.startswith((can232.CMD_TRANSMIT_EXT, can232.CMD_TRANSMIT_RTR_EXT)):  # 29bit CAN frame
                id = struct.unpack('!I', binascii.unhexlify(frame[1:9]))[0]
                length = int(frame[9:10], 16)
                if frame.startswith(can232.CMD_TRANSMIT_EXT):  # RTR frames don't have data
                    # TODO: Handle timestamp in frame if timestamp enabled..
                    data = list(binascii.unhexlify(frame[10:]))
                    type = CANMessage.DataFrame
                else:
                    # TODO: Handle timestamp in frame if timestamp enabled..
                    type = CANMessage.RemoteFrame
                can.CANFrame = CANMessage(id, length, data, True, type)
                can.CANData = True
        return can

    def do_write(self, can, params):
        """Write to the hardware."""
        if can.CANFrame.frame_type == CANMessage.DataFrame:
            if not can.CANFrame.frame_ext:  # 11bit frame
                self._C232.transmit(can.CANFrame.to_hex(), mode=can232.CAN_STANDARD)
            else:  # 29bit frame
                self._C232.transmit(can.CANFrame.to_hex(), mode=can232.CAN_EXTENDED)
        elif can.CANFrame.frame_type == CANMessage.RemoteFrame:
            if not can.CANFrame.frame_ext:  # 11bit RTR frame
                self._C232.transmit(can.CANFrame.to_hex(), mode=can232.CAN_RTR_STANDARD)
            else:  # 29bit RTR frame
                self._C232.transmit(can.CANFrame.to_hex(), mode=can232.CAN_RTR_EXTENDED)
        return can

    def do_effect(self, can, params):
        """Perform effect on the CAN bus."""
        action = params.get('action')
        if action == 'read':
            can = self.do_read(can, params)
        elif action == 'write':
            if can.CANData:
                self.do_write(can, params)
        else:
            self.dprint(0, 'Action {0} not implemented'.format(action))
        return can

    def cmd_version(self, def_in):
        """Get CAN232 version number."""
        version = self._C232.version()
        return 'CAN232 Version number: {0}. Error: {1}'.format(version.decode('ISO-8859-1'), self._C232.error)

    def cmd_serial(self, def_in):
        """Get CAN232 serial number."""
        serial = self._C232.serial()
        return 'CAN232 Serial number: {0}. Error: {1}'.format(serial.decode('ISO-8859-1'), self._C232.error)

    def cmd_open(self, def_in):
        """Open CAN232 channel."""
        self._C232.open()
        self._cmdList['t'].is_enabled = True
        self._cmdList['T'].is_enabled = True
        self._cmdList['r'].is_enabled = True
        self._cmdList['R'].is_enabled = True
        return 'CAN232 channel opened'

    def cmd_ropen(self, def_in):
        """Open CAN232 channel in read only."""
        self._C232.ropen()
        # Not possible to send CAN frames when channel in read-only.
        self._cmdList['t'].is_enabled = False
        self._cmdList['T'].is_enabled = False
        self._cmdList['r'].is_enabled = False
        self._cmdList['R'].is_enabled = False
        return 'CAN232 channel opened in read only'

    def cmd_close(self, def_in):
        """Close CAN232 channel."""
        self._C232.close()
        # Not possible to send CAN frames when channel closed.
        self._cmdList['t'].is_enabled = False
        self._cmdList['T'].is_enabled = False
        self._cmdList['r'].is_enabled = False
        self._cmdList['R'].is_enabled = False
        return 'CAN232 channel close'

    def cmd_speed(self, def_in, data):
        """Configure speed of CAN232 channel."""
        self._C232.speed(speed=data).decode('ISO-8859-1')
        return 'CAN232 Speed: {0}. Error: {1}'.format(data, self._C232.error)

    def cmd_status(self, def_in):
        """Get status CAN232 channel."""
        status = self._C232.status()
        self.dprint(1, 'Status: {0} (hex: {1})'.format(status, self.get_hex(status)))
        if self.DEBUG > 0:
            for flag in self._C232.flags.values():
                if flag[b'value']:
                    self.dprint(1, flag[b'key'])
        return 'CAN232 Status flags: {0}. Error: {1}'.format(status.decode('ISO-8859-1'), self._C232.error)

    def cmd_timestamp(self, def_in, data):
        """Enable/disable timestamps on CAN frame."""
        self._C232.timestamp(flag=data)
        return 'CAN232 timestamp switched on/off. Error: {0}'.format(self._C232.error)

    def cmd_transmit_std(self, def_in, data):
        """Send a standard CAN frame on the CAN232 channel."""
        self._C232.transmit(data, mode=can232.CAN_STANDARD)
        return 'CAN232 standard frame sent {0} (hex: {1}). Error: {2}'.format(data, self.get_hex(str.encode(data)), self._C232.error)

    def cmd_transmit_ext(self, def_in, data):
        """Send an extended CAN frame on the CAN232 channel."""
        self._C232.transmit(data, mode=can232.CAN_EXTENDED)
        return 'CAN232 extended frame sent {0} (hex: {1}). Error: {2}'.format(data, self.get_hex(str.encode(data)), self._C232.error)

    def cmd_transmit_rtr_std(self, def_in, data):
        """Send a standard RTR CAN frame on the CAN232 channel."""
        self._C232.transmit(data, mode=can232.CAN_RTR_STANDARD)
        return 'CAN232 RTR standard frame sent {0} (hex: {1}). Error: {2}'.format(data, self.get_hex(str.encode(data)), self._C232.error)

    def cmd_transmit_rtr_ext(self, def_in, data):
        """Send an extended RTR CAN frame on the CAN232 channel."""
        self._C232.transmit(data, mode=can232.CAN_RTR_EXTENDED)
        return 'CAN232 RTR extended frame sent {0} (hex: {1}). Error: {2}'.format(data, self.get_hex(str.encode(data)), self._C232.error)
