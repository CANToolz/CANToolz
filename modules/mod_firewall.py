from libs.module import *
from libs.can import *

class mod_firewall(CANModule):
    name="Filter CAN messages"
    
    help="""
    
    This module block CAN messages by ID.
    
    Init parameters:  None
    
    Module parameters: 
    
      white_list - list of ID that should be filtered
      black_list - list of ID that should not be filtered
      pipe -       integer, 1 or 2 - from which pipe to print, default 1
      
      Example: {'white_list':[133,111]}
    
    Console interrupts:
       0 or False - stop blocking
       1 or other values will enable blocking again
       
       Example (console input): c 4 f // c 4 fasle // c 4 0
    """
    
    id=4
    _block=True 
    version=1.0
    
    def rawWrite(self,data):
        if data=="false" or data=="0" or data=="False" or data[0]=="-":
            self._block=False
        else:
            self._block=True    
            
    # Effect (could be fuzz operation, sniff, filter or whatever)
    def doEffect(self, CANMsg,args={}): 
        if (CANMsg.CANData and self._block):
            if  ('black_list' in args and CANMsg.CANFrame._id in args['black_list']):
                CANMsg.CANData=False
                self.dprint(2,"Message "+str(CANMsg.CANFrame._id)+" has been blocked (BUS = "+str(CANMsg._bus)+")")
            elif ('white_list' in args and CANMsg.CANFrame._id not in args['white_list']):
                CANMsg.CANData=False
                self.dprint(2,"Message "+str(CANMsg.CANFrame._id)+" has been blocked (BUS = "+str(CANMsg._bus)+")")
        return CANMsg

