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
    _init = False
    iso = []

    def getLast(self):
        if not self.iso:
            self._active = False
            return None

        return self.iso.pop()

    def doActivate(self):
        if self._active:
            self._active = False
            self.iso = []
        else:
            self._init = True
            self._active = True

        return "Active status: " + str(self._active)

    def doPing(self, data, ISOMode, params):
        if ISOMode:
            if self._init:
                _data = [struct.unpack("B", x)[0] for x in data]
                if 'range' in params:
                    for i in range(int(params['range'][0]), int(params['range'][1])):
                        self.iso.extend(ISOTPMessage.generateCAN(i, _data))
                self.iso.reverse()
                self._init = False
        else:
            if self._init:
                _data = [struct.unpack("B", x)[0] for x in data]
                if 'range' in params:
                    for i in range(int(params['range'][0]), int(params['range'][1])):
                        self.iso.append(CANMessage.initInt(i, len(_data), _data[:8]))
                self._init = False

        CANMsgF = self.getLast()

        return CANMsgF

    def doStart(self):
        self.iso = []

    def doEffect(self, CANMsg, args={}):
        if 'body' in args:
            try:
                data = args['body'].decode('hex')
            except:
                data = "\x00" * 8
        else:
            data = "\x00" * 8

        ISOMode = False

        # Simple CAN or ISO
        if 'mode' in args:
            ISOMode = True if (args['mode'] == 'ISO' or args['mode'] == 'iso' or args['mode'] == 'ISOTP' or args[
                'mode'] == 'isotp') else False

        CANMsg.CANFrame = self.doPing(data, ISOMode, args)  # get frame

        if CANMsg.CANFrame:
            CANMsg.CANData = True
        else:
            CANMsg.CANData = False

        return CANMsg
