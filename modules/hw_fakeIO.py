from libs.can import *
from libs.module import *


class hw_fakeIO(CANModule):
    name="test I/O"

    help="""
    
    This module using for fake reading and writing CAN messages.
    No physical canal required. Used for tests. 
    
    Init parameters example:  
    
    [hw_fakeIO]
    bus = 31

        
    Module parameters: 
      action - read or write. Will write/read to/from bus
      pipe -  integer, 1 or 2 - from which pipe to read or write 
          If you use both buses(and different), than you need only one pipe configured...
        
        Example: {'action':'read','pipe':2} 
   
    """
    

    version=1.0

    CANList=None

    
    _bus=30
        
    def doStop(self): # disable reading
        self.CANList=None
   
            
    def doInit(self, params={}): # Get device and open serial port
            self._cmdList['t']=["Send direct command to the device, like 13:8:1122334455667788",1," <cmd> ",self.devWrite]
            return 1
            
    def devWrite(self, line):
        self.dprint (0,"CMD: "+line)
        id=line.split(":")[0]
        length=line.split(":")[1]
        data=line.split(":")[2]
        self.CANList=CANMessage.initInt(int(id),int(length),[struct.unpack("B",x)[0] for x in data.decode('hex')[:8]])
        return ""
        
    def doEffect(self, CANMsg,args={}): # read full packet from serial port
        if 'action' in args:
            if args['action']=='read':
                CANMsg=self.doRead(CANMsg)
            elif args['action']=='write':
                self.doWrite(CANMsg)
            else:
                dprint(1,'Command '+args['action']+' not implemented 8(')
        return CANMsg
        
     
    def doRead(self,CANMsg): 
        data=""
        if self.CANList:
            CANMsg.CANData=True
            CANMsg.CANFrame=self.CANList
            CANMsg._bus=self._bus
            self.CANList=None
            self.dprint(2,"Got message!")
        return CANMsg
        
    def doWrite(self,CANMsg): 
        if CANMsg.CANData:
            self.CANList=CANMsg.CANFrame
            self.dprint(2,"Wrote message!")
        return CANMsg
        