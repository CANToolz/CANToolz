from libs.module import *
from libs.isotp import *


class gen_ping(CANModule):
    name = "Sending CAN pings"
    help = """
    
    This module doing ID buteforce.
    (combine with mod_stat for example)
    
   
    Module parameters:  
       body           -  data HEX that will be used in CAN for discovery (by default body is 0000000000000000)
       mode           -  by default CAN, but also support ISOTP
       range          -  [0,1000] - ID range
       {'body':'0011223344556677889900aabbccddeeff','mode':'isotp'}
    """
    _active = False
    queue_messages = []

    def do_ping(self):
        if not self.queue_messages:
            self._active = False
            return None

        return self.queue_messages.pop()

    def do_start(self, args={}):
        self.queue_messages = []
        if 'body' in args:
            try:
                _data = [struct.unpack("B", x)[0] for x in (args['body'].decode('hex'))]
            except:
                _data = [0, 0, 0, 0, 0, 0, 0, 0]
        else:
            _data = [0, 0, 0, 0, 0, 0, 0, 0]

        iso_mode = False

        # Simple CAN or ISO
        if 'mode' in args:
            iso_mode = True if (args['mode'] == 'ISO' or args['mode'] == 'iso' or args['mode'] == 'ISOTP' or args[
                'mode'] == 'isotp') else False

        if 'range' in args and int(args['range'][0]) < int(args['range'][1]):
            for i in range(int(args['range'][0]), int(args['range'][1])):
                if iso_mode:
                    iso_list = ISOTPMessage.generate_can(i, _data)
                    iso_list.reverse()
                    self.queue_messages.extend(iso_list)
                else:
                    self.queue_messages.append(CANMessage.init_data(i, len(_data), _data[:8]))
        else:
            self.dprint(1, "No range specified")
            self._active = False

    def do_effect(self, can_msg, args={}):
        can_msg.CANFrame = self.do_ping()  # get frame

        if can_msg.CANFrame:
            can_msg.CANData = True
        else:
            can_msg.CANData = False

        return can_msg
