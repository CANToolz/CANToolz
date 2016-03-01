from libs.can import *

'''
dirty ISOTP impl
ISO 15765-2

https://en.wikipedia.org/wiki/ISO_15765-2

'''  
        
class ISOTPMessage():

    #PCI
    SingleFrame = 0
    FirstFrame = 1
    ConsecutiveFrame = 2
    FlowControl = 3
    
    ClearToSend = 10
    Wait = 11
    OverflowAbort = 12
    
    
    def __init__(self,id=0,length=0,data=[],finished=False): # Init EMPTY message
        self._id=id
        self._data=data
        self._length=length
        self._data=data
        self._finished=finished
        self._counterSize=0
        self._seq=0
        self._flow=-1
    
    def addCAN(self,CANMsg):   # Init  
        # The initial field is four bits indicating the frame type,
        pciType = (CANMsg._data[0] & 0xF0) >> 4 
        sz      = (CANMsg._data[0] & 0x0F)
        
        if pciType == self.SingleFrame: # Single frame
            if sz > 0 and sz < 8:
                self._data=CANMsg._data[1:sz+1]
                self._length=sz
                if sz+1 == CANMsg._length:
                    self._finished=True
                    return 1
                return -7
            else:
                return -1
        elif pciType == self.FirstFrame:     # First frame 
            self._length=(sz<<8)+CANMsg._data[1]
            if self._length>4095:
                return -6
            if self._counterSize == 0:
                self._counterSize = 6
                self._data = CANMsg._data[2:8]
                self._seq = 1      # Wait for first packet
                return 1 
            else:
                return -2
        elif pciType == self.ConsecutiveFrame: # All next frames until last one
                if sz!=self._seq:    # Wrong seq
                    return -3
                _left = self._length - self._counterSize
                _add  = min(_left,7)
                self._data.extend(CANMsg._data[1:_add+1])
                
                self._counterSize += _add
                
                if self._counterSize == self._length:
                    self._finished = True
                    return 2
                elif  self._counterSize > self._length:   
                    return -4
                    
                self._seq += 1    
                
                if self._seq > 0xF:
                    self._seq = 0    
                    
                return 2    
                
        elif pciType == self.FlowControl: 
            self._flow = sz
            return  self._flow+10
        else:
            return -5

    @classmethod   
    def generateCAN(self,id,data):   # generate CAN messages seq
        _length = len(data)
        CANMsgList = []
        
        if _length<8:
            CANMsgList.append(CANMessage.initInt(id,_length+1,[_length] + data[:_length])) # Single
        elif _length>4095:
            return []
        else:
            CANMsgList.append(CANMessage.initInt(id,8,[ (_length >> 8 ) + 0x10 ] + [_length & 0xFF] + data[:6])) # First
            seq=1
            bytes=6
            
            while  bytes != _length: # Rest
                sent = min(_length-bytes,7)
                CANMsgList.append(CANMessage.initInt(id,1+sent,[ seq + 0x20 ] + data[bytes:bytes+sent]))
                bytes+=sent
                seq+=1
                if seq  > 0xF:
                    seq = 0 
        
        return CANMsgList        
                
    