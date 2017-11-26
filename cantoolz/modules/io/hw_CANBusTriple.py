import time
import json
import struct
import serial
import serial.tools.list_ports

from cantoolz.can import CANMessage
from cantoolz.module import CANModule, Command


class hw_CANBusTriple(CANModule):

    name = "CANBus Triple I/O"
    help = """

    This module to read/write with CANBus Triple https://canb.us/.
    This device support up to 3 buses, so it is enough for MITM

    Init parameters example:

        'port' : 'auto'      # Serial port, COM3 or path.. auto also could work there
        'debug' : 2          # debug level (default 0)
        'speed' : 50         # this device support AutoRate, use auto for that

    Module parameters:
      action     - 'read' or 'write'. Will write/read to/from bus
      pipe       -  integer, 1 or 2 - from which pipe to read or write
          Example: {'action':'read','pipe':2,'bus':1}

    P.S. this device still does not support 29-bit IDs... so they will be ignored on R/W

    """

    version = 1.0

    _serialPort = None
    _COMPort = None

    _mode = 0  # 0 = RTR,11 bit

    id = 1

    def get_status(self):
        return "Current status: " + str(self._active) + "\nPORT: " + self._COMPort

    def read_all(self):
        out = ""
        while self._serialPort.inWaiting() > 0:
            out += self._serialPort.read(1).decode("ISO-8859-1")
        return out

    def get_info(self):  # Read info
        self._serialPort.write(b"\x01\x01")
        time.sleep(1)
        return self.read_all()

    def do_stop(self, params):  # disable reading
        self._serialPort.write(b"\x03\x01\x00")
        time.sleep(1)
        self._serialPort.write(b"\x03\x02\x00")
        time.sleep(1)
        self._serialPort.write(b"\x03\x03\x00")
        time.sleep(1)
        self.read_all()

    def do_exit(self, params):
        self._serialPort.close()

    def do_start(self, params):  # enable reading
        self._queue = [[], [], []]
        self._serialPort.write(b"\x03\x01\x01\x00\x00\x00\x00")
        time.sleep(1)
        self._serialPort.write(b"\x03\x02\x01\x00\x00\x00\x00")
        time.sleep(1)
        self._serialPort.write(b"\x03\x03\x01\x00\x00\x00\x00")
        time.sleep(1)

    @staticmethod
    def read_json(string):
        json1_data = json.loads(string)
        return json1_data

    def do_auto_rate(self):
        self.dprint(1, "Start AR..")

        self.do_stop({})
        self.read_all()
        self._serialPort.write(b"\x01\x0A\x01\x01")
        time.sleep(1)
        self._serialPort.write(b"\x01\x0A\x02\x00")
        time.sleep(1)
        self._serialPort.write(b"\x01\x0A\x03\x00")
        time.sleep(1)
        self._serialPort.write(b"\x03\x01\x01\x00\x00\x00\x00")
        time.sleep(1)
        self._serialPort.write(b"\x01\x08\x01")
        time.sleep(4)

        data = self.read_all().split(b"\r\n")
        x = ""
        for string in data:
            if string.find("autobaudComplete") >= 0:
                x = self.read_json(string)
        if x != "":
            self.dprint(1, "Rate for BUS 1: " + str(x['rate']))
        else:
            self.dprint(1, "Failed AR..")

        self._serialPort.write(b"\x03\x01\x00")
        time.sleep(1)

        self._serialPort.write(b"\x01\x0A\x01\x00")
        time.sleep(1)
        self._serialPort.write(b"\x01\x0A\x02\x01")
        time.sleep(1)
        self._serialPort.write(b"\x01\x0A\x03\x00")
        time.sleep(1)

        self._serialPort.write(b"\x03\x02\x01\x00\x00\x00\x00")
        time.sleep(1)
        self._serialPort.write(b"\x01\x08\x02")
        time.sleep(4)

        data = self.read_all().split(b"\r\n")
        x = ""
        for string in data:
            if string.find("autobaudComplete") >= 0:
                x = self.read_json(string)
        if x != "":
            self.dprint(1, "Rate for BUS 2: " + str(x['rate']))
        else:
            self.dprint(1, "Failed AR..")

        self._serialPort.write(b"\x03\x02\x00")
        time.sleep(1)

        self._serialPort.write(b"\x01\x0A\x01\x00")
        time.sleep(1)
        self._serialPort.write(b"\x01\x0A\x02\x00")
        time.sleep(1)
        self._serialPort.write(b"\x01\x0A\x03\x01")
        time.sleep(1)

        self._serialPort.write(b"\x03\x03\x01\x00\x00\x00\x00")
        time.sleep(1)
        self._serialPort.write(b"\x01\x08\x03")
        time.sleep(4)

        data = self.read_all().split(b"\r\n")
        x = ""
        for string in data:
            if string.find("autobaudComplete") >= 0:
                x = self.read_json(string)
        if x != "":
            self.dprint(1, "Rate for BUS 3: " + str(x['rate']))
        else:
            self.dprint(1, "Failed AR..")
        self._serialPort.write(b"\x01\x0A\x01\x01")
        time.sleep(1)
        self._serialPort.write(b"\x01\x0A\x02\x01")
        time.sleep(1)
        self._serialPort.write(b"\x01\x0A\x03\x01")
        time.sleep(1)
        self._serialPort.write(b"\x03\x03\x00")
        time.sleep(1)
        self.dprint(1, "Auto rate done...")

    def init_port(self):
        try:
            self._serialPort = serial.Serial(self._COMPort, 57600, timeout=0.5, parity=serial.PARITY_EVEN, rtscts=1)
            if (self.get_info().find("CANBus Triple")) != -1:
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
        # Interactive mode

        self.DEBUG = int(params.get('debug', 0))

        self.dprint(1, "Init phase started...")
        self._queue = [[], [], []]
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
                if self.init_port() != 1:
                    self.dprint(0, 'Can\'t init device!')
                    exit()
        else:
            self.dprint(0, 'No port in config!')
            exit()

        self.do_stop(params)
        self.read_all()
        self.dprint(1, "Port : " + self._COMPort)
        if str(params.get('speed')) != 'auto':
            self._serialPort.write(b"\x01\x09\x01" + struct.pack("!H", int(params['speed'])))
            time.sleep(1)
            self._serialPort.write(b"\x01\x09\x02" + struct.pack("!H", int(params['speed'])))
            time.sleep(1)
            self._serialPort.write(b"\x01\x09\x03" + struct.pack("!H", int(params['speed'])))
            self.dprint(1, "Speed: " + str(params.get('speed')))
        else:
            self.do_auto_rate()
        time.sleep(4)
        self.read_all()

        self.dprint(1, "CANBus Triple device detected, version: " + self.read_json(self.get_info())['version'])

        self.commands['t'] = Command("Send direct command to the device, like 02010011112233440000000008", 1, " <cmd> ", self.dev_write, True)

    def dev_write(self, data):
        self.dprint(1, "CMD: " + data)
        self._serialPort.write(bytes.fromhex(data))
        return ""

    def do_effect(self, can_msg, args):  # read full packet from serial port
        if args.get('action') == 'read':
            can_msg = self.do_read(can_msg, args)
        elif args.get('action') == 'write':
            self.do_write(can_msg, args)
        else:
            self.dprint(1, 'Command ' + args['action'] + ' not implemented 8(')
            self.set_error_text('Command ' + args['action'] + ' not implemented 8(')
        return can_msg

    def do_read(self, can_msg, args):
        data = b""
        counter = 0
        rBus = int(args.get("bus", 0))

        if 0 < rBus < 4:
            if len(self._queue[rBus - 1]) > 0:
                if not can_msg.CANData and not can_msg.debugData:
                    can_msg.CANFrame = self._queue[rBus - 1].pop(0)
                    can_msg.bus = rBus
                    can_msg.CANData = True
                    print("BUS " + str(rBus))
                    print("POP: " + str(can_msg.CANFrame))
            elif self._serialPort.inWaiting() > 0:
                while not can_msg.CANData and not can_msg.debugData:
                    byte = self._serialPort.read(1)
                    if byte == b"":
                        break

                    data += byte
                    counter += 1

                    if data[-2:] == b"\r\n":  # End
                        if data[0:1] == b'\x03' and counter == 16:  # Packet received

                            tmp_data = data[2:-3]

                            _id = struct.unpack("!H", tmp_data[0:2])[0]  # TODO: ADD SUPPORT EXTENDED and RTR
                            _data = tmp_data[2:-1]
                            _length = tmp_data[-1]
                            bus = (struct.unpack("B", data[1:2])[0])
                            if rBus == bus:
                                can_msg.CANFrame = CANMessage(_id, _length, _data, False, CANMessage.DataFrame)
                                can_msg.bus = str(self._bus) + '_' + str(bus)
                                can_msg.CANData = True
                                print("BUS " + str(rBus))
                                print("MESS:" + str(_id) + " " + str(_length) + " " + self.get_hex(_data))
                                print(self.get_hex(tmp_data))
                            else:
                                self._queue[bus - 1].append(CANMessage(_id, _length, _data, False, CANMessage.DataFrame))
                                print("BUS " + str(rBus))
                                print("QUEU:" + str(_id) + " " + str(_length) + " " + self.get_hex(_data))
                                print(self.get_hex(tmp_data))
                        elif data[0:1] == b'{' and data[-3:-2] == b'}':  # Debug info
                            can_msg.debugData = True
                            can_msg.debugText = {'text': data.decode("ISO-8859-1")}
                        else:
                            break

                        self.dprint(2, "READ: " + self.get_hex(data))
        return can_msg

    def do_write(self, can_msg, params):
        if can_msg.CANData and not can_msg.CANFrame.frame_ext and can_msg.CANFrame.frame_type == CANMessage.DataFrame:  # Only 11 bit support now..., only DataFrame
            bs = int(params.get('bus', '0'))
            if 0 < bs < 4:
                write_buf = b"\x02" + struct.pack("B", bs) + can_msg.CANFrame.frame_raw_id + \
                    can_msg.CANFrame.frame_raw_data + \
                    (b"\x00" * (8 - can_msg.CANFrame.frame_length)) + \
                    can_msg.CANFrame.frame_raw_length
                print("NUL:" + str(8 - can_msg.CANFrame.frame_length))
                print(str(can_msg.CANFrame.frame_raw_data))
            self._serialPort.write(write_buf)
            self.dprint(2, "WRITE: " + self.get_hex(write_buf))
