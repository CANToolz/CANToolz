import socket
import struct
import traceback

from cantoolz.can import CAN
from cantoolz.module import CANModule, Command


class hw_CANSocket(CANModule):

    name = "CANSocket I/O"
    help = """

    This module to read/write with CANSocket

    Init parameters example:

     'iface' : 'vcan0',       # device

    Module parameters:
      action - 'read' or 'write'. Will write/read to/from bus
      'pipe' -  integer, 1 by default - from which pipe to read or write

        Example: {'action':'read','pipe':2}
    """

    socket = None
    device = None

    def do_init(self, init_params):  # Get device and open serial port
        self.device = init_params.get('iface', None)
        self._bus = init_params.get('bus', 'CANSocket')
        self.commands['t'] = Command("Send CAN frame directly, like 01A#11223344", 1, " <frame> ", self.dev_write, True)
        self._active = True
        self._run = False

    def dev_write(self, data):
        self.dprint(1, "CMD: " + data)
        ret = "Sent!"
        if self._run:
            try:
                idf, dataf = data.strip().split('#')
                dataf = bytes.fromhex(dataf)
                idf = int(idf, 16)
                lenf = min(8, len(dataf))
                can = CAN(id=id, length=lenf, data=data[:lenf])
                self.do_write(can)
            except Exception as e:
                traceback.print_exc()
                ret = str(e)
        else:
            ret = "Module is not active!"
        return ret

    def do_start(self, params):
        if self.device and not self._run:
            try:
                self.socket = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
                self.socket.setblocking(0)
                self.socket.bind((self.device,))
                self._run = True
            except Exception as e:
                self._run = False
                self.dprint(0, "ERROR: " + str(e))
                self.set_error_text("ERROR: " + str(e))
                traceback.print_exc()

    def do_stop(self, params):
        if self.device and self._run:
            try:
                self.socket.close()
                self._run = False
            except Exception as e:
                self._run = False
                self.dprint(0, "ERROR: " + str(e))
                self.set_error_text("ERROR: " + str(e))
                traceback.print_exc()

    def do_effect(self, can, args):  # read full packet from serial port
        if args.get('action') == 'read':
            can = self.do_read(can)
        elif args.get('action') == 'write':
            can = self.do_write(can)
        else:
            self.dprint(1, 'Command ' + args['action'] + ' not implemented 8(')
        return can

    def do_read(self, can):
        if self._run and can.data is None:
            try:
                can_frame = self.socket.recv(16)
                self.dprint(2, "READ: " + self.get_hex(can_frame))
                if len(can_frame) == 16:
                    idf = struct.unpack("I", can_frame[0:4])[0]
                    if idf & 0x80000000:
                        idf &= 0x7FFFFFFF
                    length = can_frame[4]
                    can.init(id=idf, length=length, data=can_frame[8:8 + length], bus=self._bus)
            except:  # FIXME: Remove catch/all and instead catch only what needs to be caught!
                return can
        return can

    def do_write(self, can):
        if can.type == CAN.DATA:
            idf = can.id
            if can.mode == CAN.EXTENDED:
                idf |= 0x80000000
            buf = struct.pack('I', idf) + can.raw_length
            buf += b'\xff\xff\xff' + can.raw_data
            buf += b'0' * (8 - can.length)
            self.socket.send(buf)
            self.dprint(2, "WRITE: " + self.get_hex(buf))
