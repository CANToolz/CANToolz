import time
import struct
import socket
import threading
import traceback
import socketserver

from cantoolz.can import CANMessage
from cantoolz.module import CANModule, Command


class CustomTCPClient:

    def __init__(self, conn):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5.0)
        self.socket.connect(conn)
        self._thread = threading.Thread(target=self.handle)
        self._thread.daemon = True
        self._thread.start()
        self.CANList_in = []
        self.CANList_out = []
        self._access_in = threading.Event()
        self._access_out = threading.Event()

    def handle(self):
        while True:
            try:
                self.socket.sendall(b'c\x01\x00\x00')  # Request for frames
                inc_header = self.socket.recv(4)  # Get header first
                if inc_header[0:2] != b'c\x02':
                    self.selfx.dprint(0, "HEADER ERROR")
                    self.selfx.set_error_text('HEADER ERROR')
                    continue
                else:
                    ready = struct.unpack("!H", inc_header[2:4])[0]
                    inc_size = 16 * ready
                    if ready > 0:
                        inc_data = self.socket.recv(inc_size)  # Get frames
                        idx = 0
                        while ready != 0:
                            packet = inc_data[idx:idx + 16]
                            if packet[0:3] != b'ct\x03':
                                self.selfx.dprint(0, 'CLIENT GOT INCORRECT DATA')
                                self.selfx.set_error_text('CLIENT GOT INCORRECT DATA')
                                break
                            else:
                                fid = struct.unpack("!I", packet[3:7])[0]
                                flen = packet[7]
                                fdata = packet[8:16]
                                while self._access_in.is_set():
                                    time.sleep(0.0001)
                                self._access_in.set()
                                self.CANList_in.append(
                                    CANMessage.init_data(int(fid), flen, fdata)
                                )
                                self._access_in.clear()

                            idx += 16
                            ready -= 1

                while self._access_out.is_set():
                    time.sleep(0.0001)
                self._access_out.set()
                ready = len(self.CANList_out)
                if ready > 0:
                    sz = struct.pack("!H", ready)
                    send_msg = b'c\x04' + sz
                    self.socket.sendall(send_msg)
                    send_msg = b''
                    for can_msg in self.CANList_out:
                        # 16 byte
                        send_msg += b'ct\x05' + (b'\x00' * (4 - len(can_msg.frame_raw_id))) + can_msg.frame_raw_id + can_msg.frame_raw_length + can_msg.frame_raw_data + (b'\x00' * (8 - can_msg.frame_length))
                    if ready > 0:
                        self.socket.sendall(send_msg)
                        self.CANList_out = []

                self._access_out.clear()
            except Exception as e:
                self.selfx.set_error_text('TCPClient: recv response error:' + str(e))
                traceback.print_exc()

    def write_can(self, can_frame):
        while self._access_out.is_set():
            time.sleep(0.0001)
        self._access_out.set()
        self.CANList_out.append(can_frame)
        self._access_out.clear()

    def read_can(self):
        if len(self.CANList_in) > 0:
            while self._access_in.is_set():
                time.sleep(0.0001)
            self._access_in.set()
            msg = self.CANList_in.pop(0)
            self._access_in.clear()
            return msg
        else:
            return None

    def close(self):
        self._thread._stop()
        self.socket.close()


class CustomTCPServer(socketserver.TCPServer):

    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.CANList_in = []
        self.CANList_out = []
        self._access_in = threading.Event()
        self._access_out = threading.Event()
        self.socket.settimeout(5.0)
        self.prt = ""

    def write_can(self, can_frame):
        while self._access_out.is_set():
            time.sleep(0.0001)
        self._access_out.set()
        self.CANList_out.append(can_frame)

        self._access_out.clear()

    def read_can(self):
        if len(self.CANList_in) > 0:
            while self._access_in.is_set():
                time.sleep(0.0001)
            self._access_in.set()
            msg = self.CANList_in.pop(0)
            self._access_in.clear()
            return msg
        else:
            return None


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        print("TCP2CAN connected to " + str(self.server.prt))
        self.server.selfx.set_error_text("TCP2CAN connected to " + str(self.server.prt))

        self.server._access_in.clear()
        self.server._access_out.clear()

        while True:
            # Get header first
            data = self.request.recv(4)

            if data[0:1] == b'c':
                # Header
                if data[1] == 1:  # Request for frames
                    while self.server._access_out.is_set():
                        time.sleep(0.0001)
                    self.server._access_out.set()
                    ready = len(self.server.CANList_out)

                    sz = struct.pack("!H", ready)
                    send_msg = b'c\x02' + sz
                    self.request.sendall(send_msg)
                    send_msg = b''
                    for can_msg in self.server.CANList_out:
                        # 16 byte
                        send_msg += b'ct\x03' + (b'\x00' * (4 - len(can_msg.frame_raw_id))) + can_msg.frame_raw_id + can_msg.frame_raw_length + can_msg.frame_raw_data + (b'\x00' * (8 - can_msg.frame_length))
                    if ready > 0:
                        self.request.sendall(send_msg)
                        self.server.CANList_out = []

                    self.server._access_out.clear()
                elif data[1] == 4:  # Incoming frames...
                    ready = struct.unpack("!H", data[2:4])[0]
                    inc_size = 16 * ready
                    if ready > 0:
                        inc_data = self.request.recv(inc_size)
                        idx = 0
                        while ready != 0:
                            packet = inc_data[idx:idx + 16]
                            if packet[0:3] != b'ct\x05':
                                print('SERVER GOT INCORRECT DATA')
                                self.server.selfx.set_error_text('SERVER GOT INCORRECT DATA')
                                break
                            else:
                                fid = struct.unpack("!I", packet[3:7])[0]
                                flen = packet[7]
                                fdata = packet[8:16]
                                while self.server._access_in.is_set():
                                    time.sleep(0.0001)
                                self.server._access_in.set()
                                self.server.CANList_in.append(
                                    CANMessage.init_data(int(fid), flen, fdata)
                                )
                                self.server._access_in.clear()

                            idx += 16
                            ready -= 1


class hw_TCP2CAN(CANModule):

    name = "TCP interface"
    help = """

    This module works as TCP client/server for tunneling CAN Frames

    Init parameters example:
      mode  - 'client' or 'server'
      port  - <int> - TCP prt to listen or to connect (depends on mode)
      address - 'ip.ip.ip.ip' - IP address of the server

      Example: {'mode':'server','port':2001,'address':''}

    Module parameters:
      action - read or write. Will write/read to/from TCP
      pipe -  integer, 1 or 2 - from which pipe to read or write
          If you use both buses(and different), than you need only one pipe configured...

          Example: {'action':'read','pipe':2}

    """

    def get_status(self):
        return "Current status: IN: " + str(len(self.server.CANList_in)) + str(self.server._access_in.is_set()) + " OUT: " + str(len(self.server.CANList_out)) + str(self.server._access_out.is_set())

    def do_start_x(self):
        if self.server is None:
            self.dprint(2, 'Started mode as ' + str(self.mode))
            self.set_error_text('Started mode as ' + str(self.mode))
            if self.mode == 'server':
                self.server = CustomTCPServer((self.HOST, self.PORT), ThreadedTCPRequestHandler)
                self.server.prt = self.PORT
                self._thread = threading.Thread(target=self.server.serve_forever)
                self._thread.daemon = True

                self._thread.start()
            else:
                self.server = CustomTCPClient((self.HOST, self.PORT))
            self.server.selfx = self

    def do_stop_x(self):  # disable reading
        if self.server is not None:
            self.dprint(2, 'Stoped mode as ' + str(self.mode))
            self.set_error_text('Stoped mode as ' + str(self.mode))
            if self.mode == 'server':
                self.server.server_close()
                self.server.shutdown()
                self._thread._stop()
                print("DONE")
            else:
                self.server.close()
            self.server = None

    def do_init(self, params):  # Get device and open serial port
        self.commands['t'] = Command("Send direct command to the device, like 13:8:1122334455667788", 1, " <cmd> ", self.dev_write, True)

        self.mode = params.get('mode', None)
        self.server = None
        if not self.mode or self.mode not in ['server', 'client']:
            self.dprint(0, 'Can\'t get mode!')
            exit()

        self.HOST = params.get('address', 'localhost')
        self.PORT = int(params.get('port', 6550))
        self._bus = "TCP_" + self.mode + "_" + str(self.PORT)
        self.do_start_x()

        return 1

    def dev_write(self, line):
        self.dprint(0, "CMD: " + line)
        fid = line.split(":")[0]
        length = line.split(":")[1]
        data = line.split(":")[2]
        self.server.write_can(CANMessage.init_data(int(fid), int(length), bytes.fromhex(data)[:int(length)]))
        return "Sent!"

    def do_effect(self, can_msg, args):  # read full packet from serial port
        if args.get('action') == 'read':
            can_msg = self.do_read(can_msg)
        elif args.get('action') == 'write':
            self.do_write(can_msg)
        else:
            self.dprint(1, 'Command ' + args['action'] + ' not implemented 8(')
            self.set_error_text('Command ' + args['action'] + ' not implemented 8(')
        return can_msg

    def do_write(self, can_msg):
        if can_msg.CANData:
            self.server.write_can(can_msg.CANFrame)
        return can_msg

    def do_read(self, can_msg):
        if not can_msg.CANData:
            can_frame = self.server.read_can()
            if can_frame:
                can_msg.CANData = True
                can_msg.CANFrame = can_frame
                can_msg.bus = self._bus
        return can_msg
