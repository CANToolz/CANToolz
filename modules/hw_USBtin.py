from libs.can import *
from libs.module import *
import serial
import serial.tools.list_ports
import time


class hw_USBtin(CANModule):
    name = "USBtin I/O"
    help = """
    
    This module to read/write with USBtin http://www.fischl.de/usbtin/
    This device support only 1 bus, so for MITM u need one more device.
    Supporting for extended format!
    
    Init parameters example:  

     'port' : 'auto',         # Serial port
     'debug': 2,              # debug level (default 0)
     'speed': 50              # bus speed (500, 1000)

    Module parameters: 
      action - 'read' or 'write'. Will write/read to/from bus
      'pipe' -  integer, 1 by default - from which pipe to read or write

        Example: {'action':'read','pipe':2}
   
    """

    _serialPort = None
    _COMPort = None


    version = 1.0

    id = 6

    _bus = "USBTin"

    def get_info(self):  # Read info
        self._serialPort.write("S0\r")
        time.sleep(1)
        self._serialPort.write("V\r")
        time.sleep(1)
        return self.read_all()

    def read_all(self):
        out = ""
        while self._serialPort.inWaiting() > 0:
            out += self._serialPort.read(1)
        return out

    def do_stop(self, params):  # disable reading
        self._serialPort.write("C\r")
        time.sleep(1)
        self.read_all()

    def set_speed(self, speed):
        sjw_user = 3
        ## This code ported from here:
        # https://www.kvaser.com/wp-content/themes/kvaser/inc/vc/js/bittiming.js
        if len(str(speed).split(",")) > 1:
            sjw_user = int(str(speed).split(",")[1])
            self._sjw = sjw_user
            self._currentSpeed = float(str(speed).split(",")[0])
        else:
            self._currentSpeed = float(speed)
            sjw_user = self._sjw


        clock = 24 * 1000000.0
        bitrate = self._currentSpeed * 1000.0

        final_cnf1 = 0
        final_cnf2 = 0
        final_cnf3 = 0
        ch_btr0 = None
        ch_btr1 = None
        ch_btr2 = None

        matches = 0
        exactMatches = 0
        maxPrescaler = 64

        tmp = clock / bitrate / 2
        for presc  in range(1 , maxPrescaler+1):
            tmp2 = tmp / presc
            btq = round(tmp2)
            if btq >= 4 and btq <= 32:
                err = - (tmp2 / btq - 1)
                err = round(err * 10000) / 10000.0
                if (abs(err) > 0):
                    continue

                for  t1 in range(3,18):
                    t2 = btq - t1
                    if (t1 < t2) or (t2 > 8) or (t2 < 2):
                        continue
                    for sjw in range(1, 5):
                        prop = round(t1 / 2)
                        phase = t1 - prop
                        btr0 = (presc-1) + (sjw - 1) * 64
                        btr1 = (prop-2) + (phase-1) * 8 + 128
                        btr2 = t2-1

                        matches += 1
                        if err == 0:
                            ch_btr0 = struct.pack("B", btr0).encode("hex")
                            ch_btr1 = struct.pack("B", btr1).encode("hex")
                            ch_btr2 = struct.pack("B", btr2).encode("hex")

                            if sjw == sjw_user:
                                final_cnf1 = ch_btr0
                                final_cnf2 = ch_btr1
                                final_cnf3 = ch_btr2

                            exactMatches += 1

        if final_cnf1 == 0 and final_cnf2 == 0 and final_cnf3 == 0 and ch_btr0 and ch_btr1 and ch_btr2:
            final_cnf1 = ch_btr0
            final_cnf2 = ch_btr1
            final_cnf3 = ch_btr2
        if final_cnf1 == 0 and final_cnf2 == 0 and final_cnf3 == 0:
            return "Speed ERROR!"
        else:
            self.dprint(0, "CNF1 = " + final_cnf1 + " CNF2 = " + final_cnf2+" CNF3 = " + final_cnf3)
            self._serialPort.write("s" + final_cnf1 + final_cnf2 + final_cnf3 + "\r")
            return "Speed: " + str(self._currentSpeed)

    def do_start(self, params):  # enable reading
        self._serialPort.write("O\r")
        time.sleep(1)

    def init_port(self):
        try:
            self._serialPort = serial.Serial(self._COMPort, 57600, timeout=0.5, parity=serial.PARITY_EVEN, rtscts=1)

            if (self.get_info().find("V0100")) != -1:
                self.dprint(1, "Port found: " + self._COMPort)
                return 1
            else:
                self.dprint(1, "Device not found: " + self._COMPort)
                self._serialPort.close()
                return 0
        except:
            self.dprint(0, 'Error opening port: ' + self._COMPort)
            return 0

    def do_init(self, params):  # Get device and open serial port
        self.DEBUG = int(params.get('debug', 0))
        self.dprint(1, "Init phase started...")
        self._bus = (params.get('bus', "USBTin"))
        if 'port' in params:
            self._COMPort = params['port']
            if params['port'] == 'auto':
                for port in list(serial.tools.list_ports.comports()):
                    self._COMPort = port[0]
                    if self.init_port() == 1:
                        break
                if not self._serialPort:
                    self.dprint(0, 'Can\'t init device!')
                    exit()
            else:
                self.init_port()
                exit()
        else:
            self.dprint(0, 'No port in config!')
            return 0

        self.do_stop({})
        self.set_speed(str(params.get('speed', '500')) + ", " + str(params.get('sjw', '3')))
        # print str(self._serialPort)
        self.dprint(1, "PORT: " + self._COMPort)
        self.dprint(1, "Speed: " + str(self._currentSpeed))
        self.dprint(1, "USBtin device found!")

        self._cmdList['S'] = ["Set device speed (kBaud) and SJW level(optional)", 1, " <speed>,<SJW> ", self.set_speed]
        self._cmdList['t'] = ["Send direct command to the device, like t0010411223344", 1, " <cmd> ", self.dev_write]

    def dev_write(self, data):
        self.dprint(1, "CMD: " + data)
        self._serialPort.write(data + "\r")
        return ""

    def do_effect(self, can_msg, args):  # read full packet from serial port
        if args.get('action') == 'read':
            can_msg = self.do_read(can_msg)
        elif args.get('action') == 'write':
            self.do_write(can_msg)
        else:
            self.dprint(1, 'Command ' + args['action'] + ' not implemented 8(')
        return can_msg

    def do_read(self, can_msg):
        data = ""
        if self._serialPort.inWaiting() > 0:
            while not can_msg.CANData and not can_msg.debugData:
                byte = self._serialPort.read(1)
                # print byte
                if byte == "":
                    break

                data += byte
                if data[-1:] == "\r":
                    can_msg.bus = self._bus  # Bus USBtin
                    if data[0] == "t":
                        # "t10F81122334455667788"
                        _length = int(data[4])
                        _id = struct.unpack("!H", ("0" + data[1:4]).decode('hex'))[0]
                        _data = [struct.unpack("B", x)[0] for x in data[5:-1].decode('hex')]

                        can_msg.CANFrame = CANMessage(_id, _length, _data, False, CANMessage.DataFrame)

                        can_msg.CANData = True

                    elif data[0] == "T":  # Extended
                        # "T0011111181122334455667788"
                        _length = int(data[9])
                        _id = struct.unpack("!I", (data[1:9]).decode('hex'))[0]
                        _data = [struct.unpack("B", x)[0] for x in data[10:-1].decode('hex')]

                        can_msg.CANFrame = CANMessage(_id, _length, _data, True, CANMessage.DataFrame)
                        can_msg.CANData = True

                    elif data[0] == "r":  # RTR
                        _length = int(data[4])
                        _id = struct.unpack("!H", ("0" + data[1:4]).decode('hex'))[0]

                        can_msg.CANFrame = CANMessage(_id, _length, [], False, CANMessage.RemoteFrame)
                        can_msg.CANData = True

                    elif data[0] == "R":  # Extended RTR
                        _length = int(data[9])
                        _id = struct.unpack("!I", (data[1:9]).decode('hex'))[0]

                        can_msg.CANFrame = CANMessage(_id, _length, [], True, CANMessage.RemoteFrame)
                        can_msg.CANData = True
                    elif data[0] == 'z' or data[0] == 'Z' or data[0] == "\r" or data[0] == "\x07":
                        break
                    else:
                        can_msg.debugData = True
                        can_msg.debugText = {'text': data}

                    self.dprint(2, "USBtin READ: " + data)

        return can_msg

    def do_write(self, can_msg):
        if can_msg.CANData:
            cmd_byte = None
            if not can_msg.CANFrame.frame_ext and can_msg.CANFrame.frame_type == CANMessage.DataFrame:  # 11 bit format
                cmd_byte = "t"
            elif can_msg.CANFrame.frame_ext and can_msg.CANFrame.frame_type == CANMessage.DataFrame:
                cmd_byte = "T"
            elif not can_msg.CANFrame.frame_ext and can_msg.CANFrame.frame_type == CANMessage.RemoteFrame:
                cmd_byte = "r"
            elif can_msg.CANFrame.frame_ext and can_msg.CANFrame.frame_type == CANMessage.RemoteFrame:
                cmd_byte = "R"
            if cmd_byte:
                write_buf = cmd_byte + can_msg.CANFrame.frame_raw_id.encode('hex')[1:] + \
                    str(can_msg.CANFrame.frame_length) + can_msg.CANFrame.frame_raw_data.encode('hex') + "\r"
                self._serialPort.write(write_buf)
                self.dprint(2, "WRITE: " + write_buf)
        return can_msg
