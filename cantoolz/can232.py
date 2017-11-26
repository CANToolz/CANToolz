"""

Implementation of CAN232/CANUSB protocol (a.k.a LAWICEL protocol).
References:
    - http://www.can232.com/docs/canusb_manual.pdf
    - http://www.mictronics.de/projects/usb-can-bus/

Supported commands:
    - V -- Get version number
    - v -- Get detailed firmware version number
    - N -- Get serial number
    - O -- Open channel
    - L -- Open channel in read only
    - C -- Close channel
    - S -- Speed of the channel
    - F -- Get status flag
    - Z -- Switch timestamp on/off
    - t -- Transmit standard (11bit) CAN frame
    - T -- Transmit extended (29bit) CAN frame
    - r -- Transmit RTR standard (11bit) CAN frame
    - R -- Transmit RTR extended (29bit) CAN frame

"""

import time
import queue
import struct
import binascii


CAN_STANDARD = 0
CAN_EXTENDED = 1
CAN_RTR_STANDARD = 2
CAN_RTR_EXTENDED = 3

CR = b'\x0d'  # OK or end of command
BELL = b'\x07'  # Error

CAN_SPEEDS = {
    '10KBPS': b'0',
    '20KBPS': b'1',
    '50KBPS': b'2',
    '100KBPS': b'3',
    '125KBPS': b'4',
    '250KBPS': b'5',
    '500KBPS': b'6',
    '800KBPS': b'7',
    '1000KBPS': b'8',
    '83K3BPS': b'9',
}

CMD_SETUP = b'S'
CMD_VERSION = b'V'
CMD_VERSION_DETAILS = b'v'
CMD_SERIAL = b'N'
CMD_OPEN = b'O'
CMD_ROPEN = b'L'
CMD_CLOSE = b'C'
CMD_STATUS = b'F'
CMD_TIMESTAMP = b'Z'
CMD_TRANSMIT_STD = b't'
CMD_TRANSMIT_EXT = b'T'
CMD_TRANSMIT_RTR_STD = b'r'
CMD_TRANSMIT_RTR_EXT = b'R'


def force_opened(c232_cmd):
    """Decorator to enforce the CANUSB channel to be opened before performing any action."""
    def new_c232_cmd(self, *args, **kwargs):
        if not self.opened:
            self.open()
        return c232_cmd(self, *args, **kwargs)
    return new_c232_cmd


def force_closed(c232_cmd):
    """Decorator to enforce the CANUSB channel to be closed before performing any action."""
    def new_c232_cmd(self, *args, **kwargs):
        if self.opened:
            self.close()
        return c232_cmd(self, *args, **kwargs)
    return new_c232_cmd


def cache_frame(c232_cmd):
    """Decorator to force caching CAN frames if received when sending commands.

    Decorator will attempt to find all valid CAN frames in the bytes received from the CAN bus. If a CAN frame is
    detected, it is removed from the bytes received and added to the CAN232.queue list for later. If an invalid frame
    is detected (e.g. truncated for instance), it is added to the CAN232.invalid queue for later but not removed from
    the bytes received.
    """
    def new_c232_cmd(self, *args, **kwargs):
        ret = c232_cmd(self, *args, **kwargs)
        while ret:  # Find all frames in the pipe
            magic = max([ret.find(magic) for magic in [CMD_TRANSMIT_STD, CMD_TRANSMIT_EXT, CMD_TRANSMIT_RTR_STD, CMD_TRANSMIT_RTR_EXT]])
            if magic == -1:  # Not a CAN frame
                return ret
            cr = ret.find(CR)  # Looking for CR character indicating the end of a command.
            if not cr or cr < magic:  # Partial/incomplete/malformed CAN frame
                self.dprint(2, '\tInvalid frame (missing/invalid CR): {0} (hex: {1})'.format(ret, self.get_hex(ret)))
                self.invalid.put(ret)
                return ret
            frame = ret[magic:cr]
            if not self.is_valid_frame(frame):
                self.dprint(2, '\tInvalid frame (invalid): {0} (hex: {1})'.format(ret, self.get_hex(ret)))
                self.invalid.put(ret)
                return ret
            # Remove the frame processed from the data received and move on to the next one
            self.queue.put(frame)
            ret = ret[:magic] + ret[cr + 1:]
            self.dprint(2, '\tProcessed frame: {0} (hex: {1}).'.format(frame, self.get_hex(frame)))
        return ret
    return new_c232_cmd


class CAN232:

    """CAN232 class implementing support to LAWICEL protocol."""

    DEBUG = 0

    def __init__(self, serial, speed='500KBPS', timestamp=False, delay=0.2, debug=0):
        """Initialize C232 instance.

        :param serial.Serial serial: Open serial communication to the hardware.
        :param int speed: Speed of the CAN bus (See CAN_SPEEDS constants) (default: '500BKPS')
        :param boolean timestamp: Enable/disable timestamp (default: False)
        :param float delay: Time (in seconds) to wait after each serial write (default: 0.2)
        :param int debug: Level of debug (default: 0)
        """
        self.DEBUG = self.DEBUG or debug
        #: Status of the last command (True for error, False for success)
        self.error = False
        #: Queue of CAN frames received from the serial communication
        self.queue = queue.Queue()
        #: Queue of invalid data received from the serial communication
        self.invalid = queue.Queue()
        self._serial = serial
        #: Speed of the CAN bus
        self.can_speed = speed
        #: Delay after receiving data from the serial connection
        self.delay = delay
        #: Timestamps are enabled or not
        self.timestamped = timestamp
        #: Status flag of the channel
        self.flags = self._reset_flags()
        self._flush_queue()
        # Force closing any previous channel to be sure
        self.close()
        #: Status of the CAN channel (opened or not)
        self.opened = False
        self.speed()
        self.timestamp(self.timestamped)

    @staticmethod
    def _reset_flags():
        """Reset the status flag to their initial values (all set to False).

        .. warning::

            Depending on the documentation found on the internet, the status flag bits differ in terms of meaning from
            one document to another.
        """
        flags = {
            0: {b'key': b'CAN receive FIFO queue full', b'value': False},
            1: {b'key': b'CAN transmit FIFO queue full', b'value': False},
            2: {b'key': b'Error warning (EI), see SJA1000 datasheet', b'value': False},
            3: {b'key': b'Data Overrun (DOI), see SJA1000 datasheet', b'value': False},
            4: {b'key': b'Not used', b'value': False},
            5: {b'key': b'Error Passive (EPI), see SJA1000 datasheet', b'value': False},
            6: {b'key': b'Arbitration Lost (ALI), see SJA1000 datasheet', b'value': False},
            7: {b'key': b'Bus Error (BEI), see SJA1000 datasheet', b'value': False}}
        return flags

    def read(self):
        """Read every bytes available on the serial communication.

        :returns: bytes -- Bytes read from the serial link
        """
        ret = b''
        while self._serial.in_waiting > 0:
            ret += self._serial.read(1)
        self.dprint(2, '<-- Receiving: {0} (hex: {1})'.format(ret, self.get_hex(ret)))
        return ret

    @cache_frame
    def read_line(self):
        """Read a new line coming from the serial connection. Cache any valid CAN frame received."""
        ret = b''
        while True:
            c = self._serial.read(1)
            if c == b'':
                return ret
            elif c == CR:
                return ret + c
            elif c == BELL:
                return c
            else:
                ret += c

    def read_until(self, sentinel=b'', max_tries=-1):
        """Read a new line from the serial connection until finding the expected byte.

        :param bytes sentinel: Byte to wait for
        :param int max_tries: Maximum tries before giving up (default: -1 for infinite)

        :returns: bytes -- Bytes read from the line. Empty if expected bytes not foun.
        """
        ret = b''
        while max_tries:
            ret = self.read_line()
            if ret and ret[0] == sentinel[0]:
                break
            max_tries -= 1
        return ret

    def read_frame(self):
        """Fetching first frame received in the queue. If no CAN frame available, trigger a call to read_line."""
        ret = b''
        try:
            ret = self.queue.get(timeout=0.1)  # FIFO
        except queue.Empty:
            self.read_line()  # Refilling the queue
            pass
        return ret

    def write(self, data):
        """Write on the CAN232 channel.

        :param bytes data: CAN frame to send on the CAN bus.
        """
        if not data.endswith(CR):
            data += CR  # CAN232 commands always end with CR character
        self.dprint(2, '--> Sending: {0} (hex: {1})'.format(data, self.get_hex(data)))
        self._serial.write(data)
        time.sleep(self.delay)

    def _flush_queue(self):
        """Flush the CAN232 queue with empty commands as recommended in http://www.can232.com/docs/canusb_manual.pdf."""
        ret = b''
        # TODO: Expose maximum number of retries in a configuration variable.
        retries = 1
        while not ret and retries < 10:
            self.write(CR)
            ret = self.read_line()
            retries += 1
        if not ret:
            self.error = True
            self.dprint(1, 'Error when flushing the queue. Received nothing (empty response) after %d retries...' % retries)
        if BELL in ret or ret != CR:
            self.error = True
            self.dprint(1, 'Error when flushing the queue. Received: {0} (hex: {1})'.format(ret, self.get_hex(ret)))
            return ret
        self.error = False
        return ret

    def version(self, max_tries=-1):
        """Retrieve version number of CANUSB hardware.

        :param int max_tries: Maximum tries before giving up (default: -1 for infinite)

        :returns: bytes -- The version number of the CANUSB hardware.
        """
        self.write(CMD_VERSION)
        ret = self.read_until(CMD_VERSION, max_tries=max_tries)
        if len(ret) != 6 or ret[0] != CMD_VERSION[0]:
            self.error = True
            self.dprint(1, 'Error when retrieving version number. Received: {0} (hex: {1})'.format(ret, self.get_hex(ret)))
            return ret
        self.error = False
        return ret[1:-1]

    def version_details(self, max_tries=-1):
        """Retrieve detailed firmware version number of CANUSB hardware.

        :param int max_tries: Maximum tries before giving up (default: -1 for infinite)

        :returns: bytes -- The detailed firmware version number of the CANUSB hardware.
        """
        self.write(CMD_VERSION_DETAILS)
        ret = self.read_until(CMD_VERSION_DETAILS, max_tries=max_tries)
        if len(ret) != 6 or ret[0] != CMD_VERSION_DETAILS[0]:
            self.error = True
            self.dprint(1, 'Error when retrieving version number. Received: {0} (hex: {1})'.format(ret, self.get_hex(ret)))
            return ret
        self.error = False
        return ret[1:-1]

    def serial(self, max_tries=-1):
        """Retrieve serial number of CANUSB hardware.

        :param int max_tries: Maximum tries before giving up (default: -1 for infinite)

        :returns: bytes -- The serial number of the CANUSB hardware.
        """
        self.write(CMD_SERIAL)
        ret = self.read_until(CMD_SERIAL, max_tries=max_tries)
        if len(ret) != 6 or ret[0] != CMD_SERIAL[0]:
            self.error = True
            self.dprint(1, 'Error when retrieving serial number. Received: {0} (hex: {1})'.format(ret, self.get_hex(ret)))
            return ret
        self.error = False
        return ret[1:-1]

    @force_closed
    def speed(self, speed=None):
        """Setup the speed of the CAN bus.

        :params str speed: Speed of the CAN bus (default: '500KBPS')
        """
        if speed:
            speed = CAN_SPEEDS.get(speed, None)
        if speed is None:
            speed = CAN_SPEEDS.get(self.speed, CAN_SPEEDS['500KBPS'])
        self.write(CMD_SETUP + bytes(speed))
        ret = self.read_line()
        if ret != CR or ret == BELL:
            self.error = True
            self.dprint(1, 'Error when setting CAN speed. Received: {0} (hex: {1})'.format(ret, self.get_hex(ret)))
            return ret
        self.error = False
        return ret

    def open(self):
        """Open a channel with the hardware."""
        self.write(CMD_OPEN)
        ret = self.read_line()
        if ret != CR or ret == BELL:
            self.error = True
            self.dprint(1, 'Error when opening channel. Received: {0} (hex: {1})'.format(ret, self.get_hex(ret)))
            return ret
        self.opened = True
        self.error = False
        return ret

    def ropen(self):
        """Open a channel in read only with the hardware."""
        self.write(CMD_ROPEN)
        ret = self.read_line()
        if ret != CR or ret == BELL:
            self.error = True
            self.dprint(1, 'Error when opening channel in read only. Received: {0} (hex: {1})'.format(ret, self.get_hex(ret)))
            return ret
        self.opened = True
        self.error = False
        return ret

    def close(self):
        """Close a channel with the hardware."""
        self.write(CMD_CLOSE)
        ret = self.read_line()
        if ret != CR or ret == BELL:
            self.error = True
            self.dprint(1, 'Error when closing channel. Received: {0} (hex: {1})'.format(ret, self.get_hex(ret)))
            return ret
        self.opened = False
        self.error = False
        return ret

    @force_opened
    def status(self, max_tries=-1):
        """Read status flag.

        .. note::

            More human-friendly information about the status are available when accessing CAN232.flags attribute. It
            provides a description and if set/unset for each known flag.

        .. warning::

            Depending on the documentation found on the internet, the status flag bits differ in terms of meaning from
            one document to another.

        :param int max_tries: Maximum tries before giving up (default: -1 for infinite)

        :returns: bytes -- 2 bytes representing the status of the channel.
        """
        self.write(CMD_STATUS)
        ret = self.read_until(CMD_STATUS, max_tries=max_tries)
        if ret == BELL or len(ret) < 3 or ret[0] != CMD_STATUS[0]:
            self.error = True
            self.dprint(1, 'Error when retrieving status flag. Received: {0} (hex: {1})'.format(ret, self.get_hex(ret)))
            return ret
        self.flags = self._reset_flags()
        flags = struct.unpack('!B', bytes.fromhex(ret[1:-1].decode('ISO-8859-1')))[0]
        if flags & 0b00000001:
            self.flags[0][b'value'] = True
        if flags & 0b00000010:
            self.flags[1][b'value'] = True
        if flags & 0b00000100:
            self.flags[2][b'value'] = True
        if flags & 0b00010000:
            self.flags[4][b'value'] = True
        if flags & 0b00100000:
            self.flags[5][b'value'] = True
        if flags & 0b01000000:
            self.flags[6][b'value'] = True
        if flags & 0b10000000:
            self.flags[7][b'value'] = True
        self.error = False
        return ret[1:-1]

    @force_closed
    def timestamp(self, flag=False):
        """Enable/disable the timestamps.

        :param boolean flag: `True` to enable timestamp, `False` otherwise.
        """
        bit_flag = b'1'
        if not bool(flag):  # flag might be string due to module callback mechanism
            bit_flag = b'0'
        self.write(CMD_TIMESTAMP + bit_flag)
        ret = self.read_line()
        if ret == BELL or ret != CR:
            self.error = True
            self.dprint(1, 'Error when enabling/disabling timestamp. Received: {0} (hex: {1})'.format(ret, self.get_hex(ret)))
            return ret
        self.timestamped = flag  # Keep timestamp status updated only on success
        self.error = False
        return ret

    @force_opened
    def transmit(self, data, mode=CAN_STANDARD):
        """Transmit a CAN message to the bus.

        :param str data: CAN message to send.
        :param int mode: Type of CAN frame (default: CAN_STANDARD)
            - CAN_STANDARD if standard CAN frame (i.e. 11bit)
            - CAN_EXTENDED if extended (e.g. 29bit CAN frame)
            - CAN_RTR_STANDARD if standard RTR CAN frame (i.e. 11bit)
            - CAN_RTR_EXTENDED if extended RTR (e.g. 29bit CAN frame)
        """
        if isinstance(data, str):
            data = str.encode(data)
        if not self.is_valid_frame_by_type(data, mode=mode):
            self.error = True
            self.dprint(1, 'Invalid CAN frame: {0} (hex: {1})'.format(data, self.get_hex(data)))
            return BELL
        if mode == CAN_STANDARD:
            self.write(CMD_TRANSMIT_STD + data)
        elif mode == CAN_EXTENDED:
            self.write(CMD_TRANSMIT_EXT + data)
        elif mode == CAN_RTR_STANDARD:
            self.write(CMD_TRANSMIT_RTR_STD + data)
        elif mode == CAN_RTR_EXTENDED:
            self.write(CMD_TRANSMIT_RTR_EXT + data)
        else:
            self.error = True
            self.dprint(1, 'Invalid type of CAN frame: {0}'.format(self.get_hex(mode)))
            return BELL

        ret = self.read_line()
        if ret and ret != CR:
            self.error = True
            self.dprint(1, 'Error after sending CAN frame. Received: {0} (hex: {1})'.format(ret, self.get_hex(ret)))
            return ret
        self.error = False
        return ret

    def is_valid_frame_by_type(self, data, mode=CAN_STANDARD):
        """Validate a specific type of CAN frame.

        :param list data: CAN frame data
        :param int mode: CAN frame mode (standard, extended, etc.)

        :returns: boolean -- `True` if the frame is valid. `False` otherwise.
        """
        header_size = 4
        if mode == CAN_EXTENDED or mode == CAN_RTR_EXTENDED:
            header_size = 9
        if len(data) < header_size:  # Frame too small to be valid
            return False
        try:
            length = int(chr(data[header_size - 1]))
        except ValueError:  # Could occur when dealing with corrupted frame
            return False
        if length < 0 or length > 8:  # Invalid length
            return False
        if mode == CAN_STANDARD or mode == CAN_EXTENDED:  # RTR frames don't have data
            expected_length = header_size + length * 2
            expected_length += self.timestamped * 4  # Last 2 bytes are for the timestamp if enabled
            if len(data) != expected_length:  # Length of CAN payload is malformed
                return False
        return True

    def is_valid_frame(self, data):
        """Validate a CAN frame against its corresponding type detected based on the first byte.

        :returns: boolean -- `True` if the frame is at least a valid type. `False` otherwise.
        """
        if data.startswith(CMD_TRANSMIT_STD):
            return self.is_valid_frame_by_type(data[1:], mode=CAN_STANDARD)
        elif data.startswith(CMD_TRANSMIT_EXT):
            return self.is_valid_frame_by_type(data[1:], mode=CAN_EXTENDED)
        elif data.startswith(CMD_TRANSMIT_RTR_STD):
            return self.is_valid_frame_by_type(data[1:], mode=CAN_RTR_STANDARD)
        elif data.startswith(CMD_TRANSMIT_RTR_EXT):
            return self.is_valid_frame_by_type(data[1:], mode=CAN_RTR_EXTENDED)
        return False

    @staticmethod
    def get_hex(data):
        """Get hexadecimal representation of `data`.

        :params bytes data: Data to convert to hexadecimal representation.

        :returns: bytes -- Hexadecimal representation of the data
        """
        return binascii.hexlify(data)

    def dprint(self, level, msg):
        """Print function for debugging purpose."""
        if level <= self.DEBUG:
            str_msg = '{0}: {1}'.format(self.__class__.__name__, msg)
            print(str_msg)
