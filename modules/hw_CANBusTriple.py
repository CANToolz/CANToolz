from libs.can import *
from libs.module import *
import serial
import serial.tools.list_ports
import time
import json


class hw_CANBusTriple(CANModule):
    name = "CANBus Triple I/O"
    help = """
    
    This module to read/write with CANBus Triple https://canb.us/.
    This device support up to 3 buses, so it is enough for MITM
    
    Init parameters example:  
    
    [hw_CANBusTriple]
    port = auto         ; Serial port, COM3 or path.. auto also could work there
    bus_1 = 1           ; CAN bus for IO 
    ;bus_2 = 2           ; CAN bus to IO, if not commented or not equal to bus_1 then can be enough for MITM
    debug = 2          ; debug level (default 0)
    speed = 50         ; this device support AutoRate, use auto for that
        
    Module parameters: 
      action - read or write. Will write/read to/from bus
      pipe -  integer, 1 or 2 - from which pipe to read or write 
          If you use both buses(and different), than you need only one pipe configured...
          
      Example: {'action':'read','pipe':2} 
          
    P.S. this device still does not support 29-bit IDs... so they will be ignored on R/W
    
    """

    version = 1.0

    _serialPort = None
    _readBus = 0
    _writeBus = 0
    _COMPort = None
    _readBusCmd = None
    _writeBusCmd = None

    _mode = 0  # 0 = RTR,11 bit

    id = 1

    def readAll(self):
        out = ""
        while self._serialPort.inWaiting() > 0:
            out += self._serialPort.read(1)
        return out

    def getInfo(self):  # Read info
        self._serialPort.write("\x01\x01")
        time.sleep(1)
        return self.readAll()

    def doStop(self):  # disable reading
        self._serialPort.write("\x03\x01\x00")
        time.sleep(1)
        self._serialPort.write("\x03\x02\x00")
        time.sleep(1)
        self._serialPort.write("\x03\x03\x00")
        time.sleep(1)
        self.readAll()

    def doStart(self):  # enable reading
        self._serialPort.write("\x03\x01\x01\x00\x00\x00\x00")
        time.sleep(1)
        self._serialPort.write("\x03\x02\x01\x00\x00\x00\x00")
        time.sleep(1)
        self._serialPort.write("\x03\x03\x01\x00\x00\x00\x00")
        time.sleep(1)

    def readJSON(self, string):
        json1_data = json.loads(string)
        return json1_data

    def doAutoRate(self):
        self.dprint(1, "Start AR..")

        self.doStop()
        self.readAll()
        self._serialPort.write("\x01\0x0A\0x01\x01")
        time.sleep(1)
        self._serialPort.write("\x01\0x0A\0x02\x00")
        time.sleep(1)
        self._serialPort.write("\x01\0x0A\0x03\x00")
        time.sleep(1)
        self._serialPort.write("\x03\x01\x01\x00\x00\x00\x00")
        time.sleep(1)
        self._serialPort.write("\x01\x08\x01")
        time.sleep(4)

        data = self.readAll().split("\r\n")
        x = ""
        for string in data:
            if string.find("autobaudComplete") >= 0:
                x = self.readJSON(string)
        if x != "":
            self.dprint(1, "Rate for BUS 1: " + str(x['rate']))
        else:
            self.dprint(1, "Failed AR..")

        self._serialPort.write("\x03\x01\x00")
        time.sleep(1)

        self._serialPort.write("\x01\0x0A\0x01\x00")
        time.sleep(1)
        self._serialPort.write("\x01\0x0A\0x02\x01")
        time.sleep(1)
        self._serialPort.write("\x01\0x0A\0x03\x00")
        time.sleep(1)

        self._serialPort.write("\x03\x02\x01\x00\x00\x00\x00")
        time.sleep(1)
        self._serialPort.write("\x01\x08\x02")
        time.sleep(4)

        data = self.readAll().split("\r\n")
        x = ""
        for string in data:
            if string.find("autobaudComplete") >= 0:
                x = self.readJSON(string)
        if x != "":
            self.dprint(1, "Rate for BUS 2: " + str(x['rate']))
        else:
            self.dprint(1, "Failed AR..")

        self._serialPort.write("\x03\x02\x00")
        time.sleep(1)

        self._serialPort.write("\x01\0x0A\0x01\x00")
        time.sleep(1)
        self._serialPort.write("\x01\0x0A\0x02\x00")
        time.sleep(1)
        self._serialPort.write("\x01\0x0A\0x03\x01")
        time.sleep(1)

        self._serialPort.write("\x03\x03\x01\x00\x00\x00\x00")
        time.sleep(1)
        self._serialPort.write("\x01\x08\x03")
        time.sleep(4)

        data = self.readAll().split("\r\n")
        x = ""
        for string in data:
            if string.find("autobaudComplete") >= 0:
                x = self.readJSON(string)
        if x != "":
            self.dprint(1, "Rate for BUS 3: " + str(x['rate']))
        else:
            self.dprint(1, "Failed AR..")
        self._serialPort.write("\x01\0x0A\0x01\x01")
        time.sleep(1)
        self._serialPort.write("\x01\0x0A\0x02\x01")
        time.sleep(1)
        self._serialPort.write("\x01\0x0A\0x03\x01")
        time.sleep(1)
        self._serialPort.write("\x03\x03\x00")
        time.sleep(1)
        self.dprint(1, "Auto rate done...")

    def initPort(self):
        try:
            self._serialPort = serial.Serial(self._COMPort, 57600, timeout=0.5, parity=serial.PARITY_EVEN, rtscts=1)

            if (self.getInfo().find("CANBus Triple")) != -1:
                self.dprint(1, "Port found: " + self._COMPort)
                return 1
            else:
                self.dprint(1, "Device not found: " + self._COMPort)
                self._serialPort.close()
                return 0
        except:
            self.dprint(0, 'Error opening port: ' + self._COMPort)
            return 0

    def doInit(self, params={}):  # Get device and open serial port
        # Interactive mode

        if 'debug' in params:
            self.DEBUG = int(params['debug'])

        self.dprint(1, "Init phase started...")

        if 'port' in params:
            self._COMPort = params['port']
            if params['port'] == 'auto':
                for port in list(serial.tools.list_ports.comports()):
                    self._COMPort = port[0]
                    if self.initPort() == 1:
                        break
                if self._serialPort:
                    self.dprint(0, 'Can\'t init device!')
                    exit()
            else:
                self.initPort()
        else:
            self.dprint(0, 'No port in config!')
            exit()

        self.doStop()
        self.readAll()

        if 'bus_1' in params:
            self._readBus = int(params['bus_1'])

        else:
            self._readBus = 1

        self._bus = self._readBus

        if 'bus_2' in params:
            self._writeBus = int(params['bus_2'])
        else:
            self._writeBus = self._readBus

        self.dprint(1, "Port : " + self._COMPort)
        self.dprint(1, "Bus 1: " + str(self._readBus))
        self.dprint(1, "Bus 2: " + str(self._writeBus))

        if 'speed' in params and params['speed'] != 'auto':
            self._serialPort.write("\x01\x09\x01" + struct.pack("!H", int(params['speed'])))
            time.sleep(1)
            self._serialPort.write("\x01\x09\x01" + struct.pack("!H", int(params['speed'])))
            time.sleep(1)
            self._serialPort.write("\x01\x09\x01" + struct.pack("!H", int(params['speed'])))
            self.dprint(1, "Speed: " + str(params['speed']))
        else:
            self.doAutoRate()
        time.sleep(4)
        self.readAll()

        self.dprint(1, "CANBus Triple device detected, version: " + self.readJSON(self.getInfo())['version'])
        self._readBusCmd = "\x03" + str(struct.pack("B", int(self._readBus)))
        self._writeBusCmd = "\x02" + str(
            struct.pack("B", int(self._writeBus)))  # named _writeBus but just bus_2... TODO refactor to right names
        self._cmdList['t'] = ["Send direct command to the device, like 02010011112233440000000008", 1, " <cmd> ",
                              self.devWrite]

    def devWrite(self, data):
        self.dprint(1, "CMD: " + data)
        self._serialPort.write(data.decode('hex'))
        return ""

    def doEffect(self, CANMsg, args={}):  # read full packet from serial port
        if 'action' in args:
            if args['action'] == 'read':
                CANMsg = self.doRead(CANMsg)
            elif args['action'] == 'write':
                self.doWrite(CANMsg)
            else:
                self.dprint(1, 'Command ' + args['action'] + ' not implemented 8(')
        return CANMsg

    def doRead(self, CANMsg):
        data = ""
        counter = 0
        if self._serialPort.inWaiting() > 0:
            while not CANMsg.CANData and not CANMsg.debugData:
                byte = self._serialPort.read(1)
                if byte == "":
                    break

                data += byte
                counter += 1

                if data[-2:] == "\r\n":  # End
                    if data[0] == '\x03' and counter == 16:  # Packet received

                        xdata = data[2:-3]

                        _id = struct.unpack("!H", xdata[0:2])[0]  # TODO: ADD SUPPORT EXTENDED and RTR
                        _data = [struct.unpack("B", x)[0] for x in xdata[2:-1]]
                        _length = struct.unpack("B", xdata[-1])[0]

                        CANMsg.CANFrame = CANMessage(_id, _length, _data, False, CANMessage.DataFrame)

                        CANMsg._bus = int(struct.unpack("B", data[1])[0])
                        CANMsg.CANData = True

                    elif data[0] == '{' and data[-3] == '}':  # Debug info
                        CANMsg.debugData = True
                        CANMsg.debugText = data
                    else:
                        break

                    self.dprint(2, "READ: " + (data).encode('hex'))
        return CANMsg

    def doWrite(self, CANMsg):
        if CANMsg.CANData and not CANMsg.CANFrame.isExtended and CANMsg.CANFrame._type == CANMessage.DataFrame:  # Only 11 bit support now..., only DataFrame
            if CANMsg._bus == self._readBus:
                bus = self._writeBus
            elif CANMsg._bus == self._writeBus:
                bus = self._readBus
            else:
                bus = self._writeBus

            writeBuf = "\x02" + str(
                struct.pack("B", bus)) + CANMsg.CANFrame._rawId + CANMsg.CANFrame._rawData + "\x00" * \
            (8 - CANMsg.CANFrame._length) + CANMsg.CANFrame._rawLength

            self._serialPort.write(writeBuf)
            self.dprint(2, "WRITE: " + writeBuf.encode('hex'))

            return CANMsg
