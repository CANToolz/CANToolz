from cantoolz.can import CAN
from cantoolz.module import CANModule, Command


class hw_fakeIO(CANModule):

    name = "test I/O"
    help = """

    This module using for fake reading and writing CAN messages.
    No physical canal required. Used for tests.

    Init parameters example:

    Module parameters:
      action - read or write. Will write/read to/from bus
      pipe -  integer, 1 or 2 - from which pipe to read or write
          If you use both buses(and different), than you need only one pipe configured...

          Example: {'action':'read','pipe':2}

    """

    version = 1.0
    _bus = 30

    def do_start(self, params):
        self.CANList = []

    def do_stop(self, params):  # disable reading
        self.CANList = []

    def do_init(self, params):  # Get device and open serial port
        self.commands['t'] = Command("Send direct command to the device, like 13:8:1122334455667788", 1, " <cmd> ", self.dev_write, True)
        self.CANList = []
        return 1

    def dev_write(self, line):
        self.dprint(0, "CMD: " + line)
        fid = line.split(":")[0]
        length = line.split(":")[1]
        data = line.split(":")[2]
        self.CANList.append(CAN(id=int(fid), length=int(length), data=bytes.fromhex(data)[:int(length)]))
        return ''

    def do_effect(self, can, args):  # read full packet from serial port
        if args.get('action') == 'read':
            can = self.do_read(can)
        elif args.get('action') == 'write':
            can = self.do_write(can)
        else:
            self.dprint(1, 'Command ' + args['action'] + ' not implemented 8(')
        return can

    def do_write(self, can):
        if len(self.CANList) > 0:
            can = self.CANList.pop(0)
            can.bus = self._bus
            self.dprint(2, 'Got message: {}!'.format(can))
        return can

    def do_read(self, can):
        if can.data is not None:
            self.CANList.append(can)
            self.dprint(2, 'Wrote message: {}'.format(can))
        return can
