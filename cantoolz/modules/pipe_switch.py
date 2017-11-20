import copy

from cantoolz.module import CANModule


class pipe_switch(CANModule):
    name = "Switch between pipes"
    help = """

    This module can read /write/store ONE can message.

    Init parameters:  None

    Module parameters:

      'action' - read or write
            'read'  - read and store one CAN message to buffer
            'write' - write one CAN message from buffer

      Example: {'action':'read'}

    """

    _active = True
    version = 1.0

    def do_init(self, params):
        self.can_buffer = None

    def do_start(self, params):
        self.can_buffer = None

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can, args):
        if args.get('action') == 'read' and can.data is not None:
            self.can_buffer = copy.deepcopy(can)
        elif args.get('action') == 'write' and self.can_buffer:
            can = copy.deepcopy(self.can_buffer)
            self.can_buffer = None

        return can
