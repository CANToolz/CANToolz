from libs.module import *
from libs.can import *

class gen_ping(CANModule):
    name="Sending CAN pings"
    
    help="""
    
    This module doing ID buteforce.
    (combine with mod_uniqPrint for example)
    
    Init parameters:  
    
    [gen_ping]
    start_id = 1
    end_id   = 1000 
    
    Module parameters:  
       body   -  data HEX that will be used in CAN for discovery
    
    Console interrupts:
       0 or False - stop
       1 or other values will continue
       
       Example (console input): c 7 1  -- start ping
    """
    
    _i=0
    id=7
    _start=False
    fzb=[]
    
    def counter(self):
        if self._i>=len(self.fzb):
            self._i=0
            self._start=False
            self.dprint(1,"Loop finished")
        self._i+=1
        return self._i-1
        
    def rawWrite(self,data):
        if data=="false" or data=="0" or data=="False" or data[0]=="-":
            self._start=False
        else:
            self._start=True  
            
    def doInit(self, params):
        if 'start_id' in params  and 'end_id' in params:
            for i in range(int(params['start_id']),int(params['end_id'])):
                self.fzb.append(i)   
                
    def doPing(self,data,CANMsg):
        
        _data=[struct.unpack("B",x)[0] for x in data]
        CANMsg.CANFrame=CANMessage.initInt(self.fzb[self.counter()],8,_data)
        CANMsg.CANData=True
        CANMsg.debugData=False
        
        return CANMsg
        
    def doStart(self):
        self._i=0
         

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def doEffect(self, CANMsg,args={}): 
        if (self._start):
            
            if 'body' in args:
                try:
                    data =args['body'].decode('hex')
                except:
                    data = data="\x00"*8
            else:
                data="\x00"*8
                CANMsg=self.doPing(data,CANMsg)
        else:
            CANMsg.CANData=False # block all other, this is gen module
            CANMsg.debugData=False
            
        return CANMsg

