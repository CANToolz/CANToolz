from cantoolz.module import *
from cantoolz.isotp import *
import time


class gen_fuzz(CANModule):
    name = "Fuzzing one byte with shift (CAN), byte fuzz"
    help = """
    
    This module doing one-byte fuzzing for chosen shift in data.
    
    Init parameters:  None
    
    Module parameters: 

      'id'  - [0,1,2,111,333,[334,339]] - ID to fuzz. If list have sublist, than sublist should be a range
      'data'   - default data
      'delay'  - delay between frames (0 by default)
      'index'  - [1,4] - list of bytes (indexes) that should be fuzzed
      'bytes'  - bytes that will be used for fuzzing. By default all 256. If list provided, then only bytes form that list will be used.
                 If Tuple - then range
      
      Examples:
        {'id':[111,113],'data':[0,0,0,0,0,0,0,0],'delay':0, 'bytes': (0,255)}
        {'id':[111,113],'data':[0,0,0,0,0,0,0,0],'delay':0, 'bytes': [0x1,0x255]}

    """

    _i = 0
    queue_messages = []


    version = 1.0

    def do_init(self, params):
        self._active = False
        self._last = 0
        self._full = 1

    def get_status(self, def_in = 0):
        return "Current status: " + str(self._active) + "\nFrames in queue: " + str(len(self.queue_messages))

    def fuzz(self,fuzz_list, idf,data,bytes_to_fuzz,level,iso_mode):
         messages = []
         x_data = []+ data
         for byte in fuzz_list:
            x_data[bytes_to_fuzz[level]] = byte
            if level != 0:
                messages.extend(self.fuzz(fuzz_list, idf, x_data, bytes_to_fuzz, level-1, iso_mode))
            else:
                if iso_mode == 1:
                    iso_list = ISOTPMessage.generate_can(idf, x_data)
                    iso_list.reverse()
                    messages.extend(iso_list)
                else:
                    messages.append(CANMessage.init_data(idf, len(x_data), x_data[:8]))
         return messages

    def do_start(self, args):
        self._i = 0
        self.last = time.clock()
        self.queue_messages = []
        iso_mode = 1 if args.get('mode') in ['ISO', 'iso', 'ISOTP', 'isotp'] else 0
        if 'id' in args:
            for z in args['id']:
                if isinstance(z,list) and len(z)==2:
                    x = list(range(z[0], z[1]))
                elif isinstance(z, int):
                    x = [z]
                else:
                    break
                for i in x: # FOR ID
                    _body2 = list(args.get('data', []))

                    bytes_to_fuzz = args.get('index',range(0,len(_body2)))
                    bytez_for_fuzz = args.get('bytes',None)

                    if not bytez_for_fuzz:
                        fuzz_list = range(0, 255)
                    elif isinstance(bytez_for_fuzz,list):
                        fuzz_list = bytez_for_fuzz
                    elif isinstance(bytez_for_fuzz,tuple):
                        fuzz_list = range(bytez_for_fuzz[0],bytez_for_fuzz[1])
                    else:
                        fuzz_list = range(0, 255)

                    levels = len(bytes_to_fuzz)-1


                    self.queue_messages.extend(self.fuzz(fuzz_list, i,_body2,bytes_to_fuzz,levels,iso_mode))

        self._full = len(self.queue_messages)
        self._last = 0


    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if not self.queue_messages:
            self._active = False
            self.do_start(args)
        elif not can_msg.CANData:
            d_time = float(args.get('delay', 0))
            if d_time > 0:
                if time.clock() - self.last >= d_time:
                    self.last = time.clock()
                    can_msg.CANFrame = self.queue_messages.pop()
                    can_msg.CANData = True
                    can_msg.bus = self._bus
                    self._last += 1
                    self._status = self._last/(self._full/100.0)

            else:
                can_msg.CANFrame = self.queue_messages.pop()
                can_msg.CANData = True
                can_msg.bus = self._bus
                self._last += 1
                self._status = self._last/(self._full/100.0)

        return can_msg
