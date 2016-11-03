from cantoolz.module import *
from cantoolz.can import *
from random import shuffle


class mod_fuzz1(CANModule):
    name = "Proxy fuzzing one byte with chosen shift of CAN message"
    help = """
    
    This module doing one-byte fuzzing for chosen shift in data.
    
    Init parameters:  None
    
    Module parameters: 
    
      'fuzz'  - list of ID that should be fuzzed
      'nfuzz' - list of ID that should not be filtered
      'byte'  - byte index form 1 to 8, that should be fuzzed
      
      Example: {'fuzz':[133,111],'byte':1}

    """

    _i = 0
    _active = False
    version = 1.0

    def counter(self):
        if self._i >= 255:
            self._i = 0
            self._active = False
        self._i += 1
        return self._i - 1

    def do_init(self, params):
        self._active = False

    def do_start(self, params):
        self._i = 0

    # Change one byte to random
    def do_fuzz(self, can_msg, byte_to_fuzz):
        if 0 < byte_to_fuzz < 9:
            can_msg.CANFrame.frame_data[byte_to_fuzz - 1] = self.counter()
        return can_msg

    # Effect (could be fuzz operation, sniff, filter or whatever)
    # can_msg - CANToolz message from the pipe (IN)
    def do_effect(self, can_msg, args):
        # can_msg.CANData - boolean, if CANFrame in the Message
        if can_msg.CANData and can_msg.CANFrame.frame_type == CANMessage.DataFrame:
            if can_msg.CANFrame.frame_id in args.get('fuzz', []) and 'byte' in args:
                can_msg = self.do_fuzz(can_msg, args['byte'])
                can_msg.bus = self._bus
            elif 'nfuzz' in args and can_msg.CANFrame.frame_id not in args.get('nfuzz', []) and 'byte' in args:
                can_msg = self.do_fuzz(can_msg, args['byte'])
                can_msg.bus = self._bus
        # can_msg - CANToolz message TO the pipe (out)
        return can_msg
