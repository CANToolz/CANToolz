from libs.can import *
from libs.module import *
#from libs.engine import struct
import serial
import serial.tools.list_ports
import time

class hw_USBtin(CANModule):
    name="USBtin I/O"

    help="""
    
    This module to read/write with USBtin http://www.fischl.de/usbtin/
    This device support only 1 bus, so for MITM u need one more device.
    Supporting for extended format!
    
    Init parameters example:  
    
    [hw_USBtin]
    port = auto         ; Serial port
    debug = 2           ; debug level (default 0)
    speed = 50         ; bus speed (500, 1000)

        
    Module parameters: 
      action - read or write. Will write/read to/from bus
      pipe -  integer, 1 or 2 - from which pipe to read or write 
          If you use both buses(and different), than you need only one pipe configured...
    
    Console interrupts:
       Write to serial port of CANBus Triple device
       
       Example - send CAN  (console input): c 6 t0ff81122334455667788

    
    """
    
    _serialPort=None
    _COMPort=None
    _speed={500:'S6\r',1000:'S8\r',10:'S0\r',100:'S3\r',50:'S2\r'}
    _currentSpeed=10
    version=1.0

    id=6
    
    _bus=60
   
    def getInfo(self): # Read info
        self._serialPort.write("S0\r")
        time.sleep(1)
        self._serialPort.write("V\r")
        time.sleep(1)
        return self.readAll()
        
    def readAll(self):
        out=""
        while self._serialPort.inWaiting() > 0:
            out+= self._serialPort.read(1)   
        return out  
        
    def doStop(self): # disable reading
        self._serialPort.write("C\r")
        time.sleep(1)
        self.readAll()
        
    def doStart(self):# enable reading
        self._serialPort.write(self._speed[self._currentSpeed]+"\r")
        time.sleep(1)
        self._serialPort.write("O\r")
        time.sleep(1)
    
    def initPort(self):
        try:
            self._serialPort = serial.Serial(self._COMPort,57600, timeout=0.5, parity=serial.PARITY_EVEN, rtscts=1)

            if (self.getInfo().find("V0100"))!=-1:
                self.dprint(1,"Port found: "+self._COMPort)
                return 1;
            else:
                self.dprint(1,"Device not found: "+self._COMPort)
                self._serialPort.close()
                return 0;
        except:
            self.dprint(0,'Error opening port: '+self._COMPort)
            return 0
            
    def doInit(self, params={}): # Get device and open serial port
            # Interactive mode
            
            if 'debug' in params:
                self.DEBUG=int(params['debug'])
            
            self.dprint( 1,"Init phase started...")
                
                
            if 'port' in params:
                self._COMPort=params['port']
                if params['port']=='auto':
                    for port in list(serial.tools.list_ports.comports()):
                        self._COMPort=port[0]
                        if self.initPort()==1:
                            break
                    if self._serialPort==None:
                        self.dprint(0,'Can\'t init device!')
                        exit()        
                else:
                    self.initPort()
                    exit()
            else:
                self.dprint(0,'No port in config!')
                return 0
                
            self.doStop()   
            #data=self.readAll()
            if 'speed' in params:
                self._currentSpeed=int(params['speed'])
            else:
                self._currentSpeed=50
                   
            #print str(self._serialPort)
            self.dprint(1, "PORT: "+self._COMPort)
            self.dprint(1, "Speed: "+str(self._currentSpeed))
         
            self.dprint (1,"USBtin device found!")
            
    def rawWrite(self, data):
        self.dprint (1,"CMD: "+data)
        self._serialPort.write(data+"\r")
        
    def doEffect(self, CANMsg,args={}): # read full packet from serial port
        if args['action']=='read':
            CANMsg=self.doRead(CANMsg)
        elif args['action']=='write':
            self.doWrite(CANMsg)
        else:
            dprint(1,'Command '+args['action']+' not implemented 8(')
        return CANMsg
        
     
    def doRead(self,CANMsg): 
        data=""
        counter=0
        if self._serialPort.inWaiting()>0:
            while not CANMsg.CANData and not CANMsg.debugData: 
                byte=self._serialPort.read(1)
                if byte=="":
                    break;
                    
                data += byte

                if data[-1:]=="\r":
                    CANMsg._bus=self._bus # Bus USBtin as BUS 60...
                    
                        
                    if data[0]=="t": 
                    
                        
                        #"t10F81122334455667788"
                        _length=int(data[4])
                        _id=struct.unpack("!H",("0"+data[1:4]).decode('hex'))[0]
                        _data=[struct.unpack("B",x)[0] for x in data[5:-1].decode('hex')] 
                        
                        CANMsg.CANFrame=CANMessage(_id,_length,_data,False,CANMessage.DataFrame)

                        CANMsg.CANData=True
                        
                    elif data[0]=="T": # Extended
                        
                        #"T0011111181122334455667788"
                        _length=int(data[9])
                        _id=struct.unpack("!I",(data[1:9]).decode('hex'))[0]
                        _data=[struct.unpack("B",x)[0] for x in data[10:-1].decode('hex')] 
                                      
                        CANMsg.CANFrame=CANMessage(_id,_length,_data,True,CANMessage.DataFrame)
                        CANMsg.CANData=True
                        
                    elif data[0]=="r": # RTR
                                         
                        _length=int(data[4])
                        _id=struct.unpack("!H",("0"+data[1:4]).decode('hex'))[0]
                        
                        CANMsg.CANFrame=CANMessage(_id,_length,[],False,CANMessage.RemoteFrame)
                        CANMsg.CANData=True
                        
                    elif data[0]=="R": # Extended RTR 
                        _length=int(data[9])
                        _id=struct.unpack("!I",(data[1:9]).decode('hex'))[0]
                        
                        CANMsg.CANFrame=CANMessage(_id,_length,[],True,CANMessage.RemoteFrame)
                        CANMsg.CANData=True
                    elif data[0]=='z' or data[0]=='Z' or data[0]=="\r" or data[0]=="\x07": 
                        break    
                    else: 
                        CANMsg.debugData=True
                        CANMsg.debugText=data
                        
                    self.dprint (2,"USBtin READ: "+data)      
          
        return CANMsg
        
    def doWrite(self,CANMsg): 
        if CANMsg.CANData:
            cmdByte=None

            if not CANMsg.CANFrame.isExtended and CANMsg.CANFrame._type==CANMessage.DataFrame: # 11 bit format
                cmdByte="t"
            elif CANMsg.CANFrame.isExtended and CANMsg.CANFrame._type==CANMessage.DataFrame:   
                cmdByte="T"
            elif not CANMsg.CANFrame.isExtended and CANMsg.CANFrame._type==CANMessage.RemoteFrame:
                cmdByte="r"
            elif CANMsg.CANFrame.isExtended and CANMsg.CANFrame._type==CANMessage.RemoteFrame:
                cmdByte="R"    
            if cmdByte:    
                writeBuf = cmdByte+CANMsg.CANFrame._rawId.encode('hex')[1:]+str(CANMsg.CANFrame._length)+(CANMsg.CANFrame._rawData).encode('hex')+"\r"
                self._serialPort.write(writeBuf)
                self.dprint (2,"WRITE: "+writeBuf)
        return CANMsg
        