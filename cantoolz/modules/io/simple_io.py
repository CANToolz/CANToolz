from cantoolz.can import CAN
from cantoolz.module import CANModule, Command


class simple_io(CANModule):

    name = "Simple read/werite module"
    help = """

    This module can read/write and store message.

    Init parameters:  None

    Module parameters:

      none

      Example: {'action':'read'}

    """

    _active = True

    def do_init(self, params):
        self.can_buffer_read = []
        self.can_buffer_write = []
        self.commands['c'] = Command("Clean buffers", 0, "", self.do_start, True)
        self.commands['r'] = Command("Read message", 0, "", self.cmd_read, True)
        self.commands['w'] = Command("Write message", 1, "[0x]ID[:len]:HEX_DATA", self.cmd_write, True)

    def get_status(self):
        return "Current status: " + str(self._active) + "\nFrames to read: " + str(len(self.can_buffer_read)) + "\nFrames to write: " + str(len(self.can_buffer_write))

    def cmd_write(self, frame):
        frame = frame.strip().split(":")
        fid = frame[0].strip()

        fid = int(fid, 0)

        if len(frame) == 2:
            length = len(bytes.fromhex(frame[1].strip()))
            data = bytes.fromhex(frame[1].strip())
        elif len(frame) == 3:
            length = int(frame[1].strip())
            data = bytes.fromhex(frame[2].strip())
        else:
            return 'Bad format'
        self.can_buffer_write.append(CAN(id=fid, length=length, data=data))
        return 'Added to queue'

    def cmd_read(self):
        ret = 'None'
        if len(self.can_buffer_read) > 0:
            can = self.can_buffer_read.pop(0)
            ret = hex(can.id) + ":" + str(can.length) + ":" + self.get_hex(can.raw_data)
        return ret

    def do_start(self, params):
        self.can_buffer = []
        self.can_buffer_write = []

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can, args):
        if can.data is not None:
            self.can_buffer_read.append(can)
        elif len(self.can_buffer_write) > 0:
            can = self.can_buffer_write.pop(0)
            can.bus = self._bus
        return can
