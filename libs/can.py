import struct
'''
Generic class for CAN message
'''  
        
class CANMessage():

    DataFrame = 1
    RemoteFrame = 2
    ErrorFrame = 3
    OverloadFrame = 4
 
    def __init__(self,id,length,data,extended,type): # Init EMPTY message

          
        self._id=id          # Message ID       
        self._length=length  # DATA length 
        self._data=data      # DATA

        self._ext=extended   # 29 bit message ID - boolean flag
        
        self._type=type      
        self.parseParams()
        
    @classmethod     
    def initInt(self,id,length,data):   # Init    
        if length > 8:
            length = 8
        if id >= 0 and id <= 0x7FF: 
            extended = False
        elif id > 0x7FF and id < 0x1FFFFFFF:
            extended = True
        else:
            id = 0
   
        return CANMessage(id,length,data,extended,1)  

    @classmethod    
    def initStr(self,id,length,data):   # Another way to init from raw data
    
        if len(id)==2: 
            extended = False
        else:
            extended = True
   
        temp = CANMessage(0,0,[],extended,1)  
        
        temp._rawId=id
        temp._rawlength=length
        temp._rawData=data
        
        temp.parseRaw()
        
        return temp
        
    @property    
    def isExtended(self):
        return self._ext
        
    def parseParams(self):    
    
        if not self._ext:
            self._rawId=struct.pack("!H",self._id)
        else:
            self._rawId=struct.pack("!I",self._id)
        
        self._rawLength=struct.pack("!B",self._length)
        self._rawData=''.join(struct.pack("!B",b) for b in self._data)
            
    def parseRaw(self):
     
        if not self._ext:
            self._id = struct.unpack("!H",self._rawId)[0]    
        else:
            self._id = struct.unpack("!I",self._rawId)[0]
        
        self._length = struct.unpack("B",self._rawLength)[0]
        self._data = [struct.unpack("B",x)[0] for x in _rawData]

        
        
'''
Class to handle CAN messages and other data
'''          
class CANSploitMessage:   
     
    def __init__(self): # Init EMPTY message

        self.debugText=""
        self.CANFrame=None
        self.debugData=False
        self.CANData=False
        self._bus=0
        