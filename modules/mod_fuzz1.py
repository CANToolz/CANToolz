from libs.module import *
from libs.can import *
from random import shuffle

class mod_fuzz1(CANModule):
    name="Fuzzing one byte with chosen shift of CAN message"
    
    help="""
    
    This module doing one-byte fuzzing for chosen shift in data.
    
    Init parameters:  None
    
    Module parameters: 
    
      fuzz  - list of ID that should be fuzzed
      nfuzz - list of ID that should not be filtered
      byte  - byte index form 1 to 8, that should be fuzzed
      
      Example: {'fuzz':[133,111],'byte':1}
    
    Console interrupts:
       0 or False - stop fuzzing
       1 or other values will enable fuzzing again
       
       Example (console input): c 4 f // c 4 fasle // c 4 0
    """
    
    _i=0
    fzb=[]
    id=2
    _fuzz=True 
    
    version=1.0
    
    def counter(self):
        if self._i>=255:
            self._i=0
            
        self._i+=1
        return self._i-1
        
    def doInit(self, params):
        for i in range(0,255):
            self.fzb.append(i)
            
    def rawWrite(self,data):
        if data=="false" or data=="0" or data=="False" or data[0]=="-":
            self._fuzz=False
        else:
            self._fuzz=True   
            
    # Change one byte to random        
    def doFuzz(self, CANMsg, shift):
        if shift > 0 and shift < 9 and self._fuzz:
            CANMsg.CANFrame._data[shift-1]=self.fzb[self.counter()]
            CANMsg.CANFrame.parseParams()
            self.dprint(2,"Message "+str(CANMsg.CANFrame._id)+" has been fuzzed (BUS = "+str(CANMsg._bus)+")")

        return CANMsg
        
    def doStart(self):
        self._i=0
        shuffle(self.fzb)
        
    # Effect (could be fuzz operation, sniff, filter or whatever)
    def doEffect(self, CANMsg,args={}): 
        if (CANMsg.CANData and CANMsg.CANFrame._type==CANMessage.DataFrame):
            if ('fuzz' in args and CANMsg.CANFrame._id in args['fuzz'] and 'byte' in args):
                    CANMsg=self.doFuzz(CANMsg,args['byte']);
            elif ('nfuzz' in args and CANMsg.CANFrame._id not in args['nfuzz'] and 'byte' in args):
                    CANMsg=self.doFuzz(CANMsg,args['byte']);
        return CANMsg

