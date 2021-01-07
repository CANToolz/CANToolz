import time
import struct
import serial
import traceback
import serial.tools.list_ports

from cantoolz.can import CANMessage
from cantoolz.module import CANModule, Command


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

    def get_status(self):
        return "Current status: " + str(self._active) + "\nCurrent SPEED: " + str(self._currentSpeed) + "\nPORT: " + self._COMPort + "\nLost frames: " + str(self._lost_frames)

    def get_info(self):  # Read info
        self._serialPort.write(b"S0\r")
        time.sleep(1)
        self._serialPort.write(b"V\r")
        time.sleep(1)
        return self.read_all()

    def read_all(self):
        out = ""
        while self._serialPort.inWaiting() > 0:
            out += self._serialPort.read(1).decode("ISO-8859-1")
        return out

    def do_stop(self, params):  # disable reading
        if self._run:
            self.dev_write("C")
            self._run = False
        time.sleep(1)
        self.read_all()

    def set_speed(self, speed):
        sjw_user = 3
        # This code ported from https://www.kvaser.com/wp-content/themes/kvaser/inc/vc/js/bittiming.js
        again = False
        if self._run:
            self._active = False
            self.do_stop({})
            again = True

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
        for presc in range(1, maxPrescaler + 1):
            tmp2 = tmp / presc
            btq = round(tmp2)
            if btq >= 4 and btq <= 32:
                err = - (tmp2 / btq - 1)
                err = round(err * 10000) / 10000.0
                if abs(err) > 0:
                    continue

                for t1 in range(3, 18):
                    t2 = btq - t1
                    if (t1 < t2) or (t2 > 8) or (t2 < 2):
                        continue
                    for sjw in range(1, 5):
                        prop = round(t1 / 2)
                        phase = t1 - prop
                        btr0 = (presc - 1) + (sjw - 1) * 64
                        btr1 = (prop - 2) + (phase - 1) * 8 + 128
                        btr2 = t2 - 1

                        matches += 1
                        if err == 0:
                            ch_btr0 = self.get_hex(struct.pack("B", btr0)).encode("ISO-8859-1")
                            ch_btr1 = self.get_hex(struct.pack("B", btr1)).encode("ISO-8859-1")
                            ch_btr2 = self.get_hex(struct.pack("B", btr2)).encode("ISO-8859-1")

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
            if again:
                self.do_start({})
                self._active = True

            return "Speed ERROR!"
        else:
            self.dprint(0, "CNF1 = " + final_cnf1.decode("ISO-8859-1") + " CNF2 = " + final_cnf2.decode("ISO-8859-1") + " CNF3 = " + final_cnf3.decode("ISO-8859-1"))
            self._serialPort.write(b"s" + final_cnf1 + final_cnf2 + final_cnf3 + b"\r")
            if again:
                self.do_start({})
                self._active = True
            return "Speed: " + str(self._currentSpeed)

    def do_start(self, params):  # enable reading

        if not self._run:
            if not self._usbtin_loop:
                self.dev_write("O")
            else:
                self.dev_write("l")
            self._run = True
            self.wait_for = False
            self.last = time.process_time()
        time.sleep(1)

    def init_port(self):
        try:
            self._serialPort = serial.Serial(self._COMPort, 57600, timeout=0.5, write_timeout=1, writeTimeout=1, parity=serial.PARITY_EVEN, rtscts=1)
            if (self.get_info().find("V0100")) != -1:
                self.dprint(1, "Port found: " + self._COMPort)
                return 1
            else:
                self.dprint(1, "Device not found: " + self._COMPort)
                self._serialPort.close()
                return 0
        except Exception as e:
            self.dprint(0, 'Error opening port: ' + self._COMPort + str(e))
            return 0

    def do_exit(self, params):
        self._serialPort.close()

    def do_init(self, params):  # Get device and open serial port
        self.DEBUG = int(params.get('debug', 0))
        self.dprint(1, "Init phase started...")
        self._bus = (params.get('bus', "USBTin"))
        self._lost_frames = 0
        self._dev_write_try = 0
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
            elif params['port'] == 'loop':
                self._serialPort = serial.serial_for_url('loop://', timeout=0.5)
            else:
                if self.init_port() != 1:
                    self.dprint(0, 'Can\'t init device!')
                    exit()
        else:
            self.dprint(0, 'No port in config!')
            return 0
        self._usbtin_loop = bool(params.get('usbtin_loop', False))
        self._restart = bool(params.get('auto_activate', False))
        self.act_time = float(params.get('auto_activate', 5.0))
        self.last = time.process_time()
        self.wait_for = False
        self._run = True
        self.do_stop({})
        self.set_speed(str(params.get('speed', '500')) + ", " + str(params.get('sjw', '3')))
        # print str(self._serialPort)
        self.dprint(1, "PORT: " + self._COMPort)
        self.dprint(1, "Speed: " + str(self._currentSpeed))
        self.dprint(1, "USBtin device found!")

        self.commands['speed'] = Command("Set device speed (kBaud) and SJW level(optional)", 1, " <speed>,<SJW> ", self.set_speed, True)
        self.commands['t'] = Command("Send direct command to the device, like t001411223344", 1, " <cmd> ", self.dev_write, True)

    def dev_write(self, data):
        self.dprint(2, "CMD: " + data + " try: " + str(self._dev_write_try))
        try:
            self._serialPort.write(data.encode("ISO-8859-1") + b"\r")
        except Exception as e:
            self.dprint(2, "USBTin ERROR: can't write...")
            if self._dev_write_try < 6:
                self.dprint(1, "USBTin restart")
                try:
                    self._serialPort.close()
                    time.sleep(1)
                    self._serialPort = serial.Serial(self._COMPort, 57600, timeout=0.5, write_timeout=1, writeTimeout=1, parity=serial.PARITY_EVEN, rtscts=1)
                    time.sleep(1)
                    self.do_start({})
                    self._dev_write_try += 1
                    self.dev_write(data)
                except Exception as e2:
                    self._dev_write_try = 0
                    self.dev_write("USBTIn ERROR: can't reopen - \n\t" + str(e) + "\n\t" + str(e2))
                    self.set_error_text("USBTIn ERROR: can't reopen - \n\t" + str(e) + "\n\t" + str(e2))
                    traceback.print_exc()

            else:
                self._dev_write_try = 0
                self.dev_write("USBTIn ERROR")
                self.set_error_text('USBTIn ERROR I/O')
        return ""

    def do_effect(self, can_msg, args):  # read full packet from serial port
        if args.get('action') == 'read':
            can_msg = self.do_read(can_msg)
        elif args.get('action') == 'write':
            # KOSTYL: workaround for BMW f10 bus
            # if self._restart and self._run and (time.process_time() - self.last) >= self.act_time:
            #     self.dev_write("O")
            #     self.last = time.process_time()
            self.do_write(can_msg)
        else:
            self.dprint(1, 'Command ' + args.get('action', 'NONE') + ' not implemented 8(')
            self.set_error_text('Command ' + args.get('action', 'NONE') + ' not implemented 8(')

        """
        if self._restart:
                if self.wait_for and can_msg.debugData and can_msg.debugText['text'][0] == "F" and len(can_msg.debugText['text']) > 2:
                    error = int(can_msg.debugText['text'][1:3],16)
                    self.dprint(1,"BUS ERROR:" + hex(error))
                    if error & 8: # Fix for BMW CAN where it could be overloaded
                       self.dev_write("C")
                       time.sleep(0.4)
                       self.dev_write("O")
                       can_msg.debugText['do_not_send'] = True
                    else:
                       can_msg.debugText['please_send'] = True
                    self.wait_for = False

                elif time.process_time() - self.last >= self.act_time and not self.wait_for:
                    self.dev_write("F")
                    self.wait_for = True
                    self.last = time.process_time()
        """

        return can_msg

    def do_read(self, can_msg):
        data = b""
        if self._serialPort.inWaiting() > 0:
            while not can_msg.CANData and not can_msg.debugData:
                byte = self._serialPort.read(1)
                if byte == b"":
                    break

                data += byte
                if data[-1:] == b"\r":
                    can_msg.bus = self._bus  # Bus USBtin
                    if data[0:1] == b"t":
                        # "t10F81122334455667788"
                        _length = int(data[4:5])
                        _id = struct.unpack("!H", bytes.fromhex("0" + data[1:4].decode('ISO-8859-1')))[0]
                        _data = list(bytes.fromhex(data[5:-1].decode('ISO-8859-1')))

                        can_msg.CANFrame = CANMessage(_id, _length, _data, False, CANMessage.DataFrame)

                        can_msg.CANData = True

                    elif data[0:1] == b"T":  # Extended
                        # "T0011111181122334455667788"
                        _length = int(data[9:10])
                        _id = struct.unpack("!I", bytes.fromhex(data[1:9].decode('ISO-8859-1')))[0]
                        _data = list(bytes.fromhex(data[10:-1].decode('ISO-8859-1')))

                        can_msg.CANFrame = CANMessage(_id, _length, _data, True, CANMessage.DataFrame)
                        can_msg.CANData = True

                    elif data[0:1] == b"r":  # RTR
                        _length = int(data[4:5])
                        _id = struct.unpack("!H", bytes.fromhex("0" + data[1:4].decode('ISO-8859-1')))[0]

                        can_msg.CANFrame = CANMessage(_id, _length, [], False, CANMessage.RemoteFrame)
                        can_msg.CANData = True

                    elif data[0:1] == b"R":  # Extended RTR
                        _length = int(data[9:10])
                        _id = struct.unpack("!I", bytes.fromhex(data[1:9].decode('ISO-8859-1')))[0]

                        can_msg.CANFrame = CANMessage(_id, _length, [], True, CANMessage.RemoteFrame)
                        can_msg.CANData = True

                    elif data[0:1] == b"z" or data[0:1] == b"Z" or data[0:1] == b"\r" or data[0:1] == b"\x07":
                        break
                    else:
                        can_msg.debugData = True
                        can_msg.debugText = {'text': data.decode("ISO-8859-1")}
                        self.dprint(1, "USBtin DREAD: " + data.decode("ISO-8859-1"))

                    self.dprint(2, "USBtin READ: " + data.decode("ISO-8859-1"))

        return can_msg

    def do_write(self, can_msg):

        if can_msg.CANData:
            self.dprint(3, "WRITE")
            cmd_byte = None
            id_f = None
            if not can_msg.CANFrame.frame_ext and can_msg.CANFrame.frame_type == CANMessage.DataFrame:  # 11 bit format
                cmd_byte = b"t"
                id_f = self.get_hex(can_msg.CANFrame.frame_raw_id).zfill(4)[1:4].encode('ISO-8859-1')
            elif can_msg.CANFrame.frame_ext and can_msg.CANFrame.frame_type == CANMessage.DataFrame:
                cmd_byte = b"T"
                id_f = self.get_hex(can_msg.CANFrame.frame_raw_id).zfill(8)[0:8].encode('ISO-8859-1')
            elif not can_msg.CANFrame.frame_ext and can_msg.CANFrame.frame_type == CANMessage.RemoteFrame:
                cmd_byte = b"r"
                id_f = self.get_hex(can_msg.CANFrame.frame_raw_id).zfill(4)[1:4].encode('ISO-8859-1')
            elif can_msg.CANFrame.frame_ext and can_msg.CANFrame.frame_type == CANMessage.RemoteFrame:
                cmd_byte = b"R"
                id_f = self.get_hex(can_msg.CANFrame.frame_raw_id).zfill(8)[0:8].encode('ISO-8859-1')
            if cmd_byte:
                write_buf = cmd_byte + id_f + str(can_msg.CANFrame.frame_length).encode('ISO-8859-1') + self.get_hex(can_msg.CANFrame.frame_raw_data).encode('ISO-8859-1') + b"\r"
                self.dprint(2, "Try to write: " + write_buf.decode('ISO-8859-1'))
                self._dev_write_try = 2
                self.dev_write(write_buf.decode('ISO-8859-1')[:-1])
                self.dprint(2, "WRITE: " + write_buf.decode('ISO-8859-1'))
        return can_msg
