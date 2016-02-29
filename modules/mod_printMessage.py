from libs.module import *
from libs.can import *

class mod_printMessage(CANModule):
    name="Print CAN message"
    
    help="""
    
    This module do only printing CAN messages and Debug info.
    
    Init parameters:  None
    
    Module configuration: 
    
      white_list - list of ID that should be printed
      black_list - list of ID that should not be printed
      pipe       - integer, 1 or 2 - from which pipe to print, default 1
      
      Example: {'white_list':[133,111]}
    
    """
    _active=True
    
    id=5

    version=1.0
    
        
    # Effect (could be fuzz operation, sniff, filter or whatever)
    def doEffect(self, CANInput,args={}):
        
        if CANInput.CANData:
            if 'white_list' in args:
                if CANInput.CANFrame._id in args['white_list']:
                    print("Read: "+self.doRead(CANInput)); # Print CAN Message
            elif 'black_list' in args: 
                if CANInput.CANFrame._id not in args['black_list']:
                    print("Read: "+self.doRead(CANInput)); # Print CAN Message
            else:
                print("Read: "+self.doRead(CANInput)); # Print CAN Message
        elif not CANInput.CANData and CANInput.debugData:
            self.dprint(1,"DEBUG: "+CANInput.debugText)
        return CANInput

    def doRead(self,CANInput): 
            return  "BUS = "+str(CANInput._bus)+" ID = "+str(CANInput.CANFrame._id)+" Message: "+ str(CANInput.CANFrame._rawData).encode('hex')+" Len: "+str(CANInput.CANFrame._length)
        
