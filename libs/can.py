import struct

'''
Generic class for CAN message
'''


class CANMessage:
    DataFrame = 1
    RemoteFrame = 2
    ErrorFrame = 3
    OverloadFrame = 4

    def __init__(self, fid, length, data, extended, type):  # Init EMPTY message
        self.frame_id = fid  # Message ID
        self.frame_length = length  # DATA length
        self.frame_data = data  # DATA
        self.frame_ext = extended  # 29 bit message ID - boolean flag

        self.frame_type = type

        self.frame_raw_id = ''
        self.frame_raw_length = ''
        self.frame_raw_data = ''

        self.parse_params()

    @classmethod
    def init_data(self, fid, length, data):  # Init
        if length > 8:
            length = 8
        if 0 <= fid <= 0x7FF:
            extended = False
        elif 0x7FF < fid < 0x1FFFFFFF:
            extended = True
        else:
            fid = 0
            extended = False

        return CANMessage(fid, length, data, extended, 1)

    @classmethod
    def init_raw_data(self, fid, length, data):  # Another way to init from raw data

        if len(fid) == 2:
            extended = False
        else:
            extended = True

        temp = CANMessage(0, 0, [], extended, 1)

        temp.set_raw_id = fid
        temp.set_raw_length = length
        temp.set_raw_data = data

        temp.parse_raw()

        return temp

    def parse_params(self):

        if not self.frame_ext:
            self.frame_raw_id = struct.pack("!H", self.frame_id)
        else:
            self.frame_raw_id = struct.pack("!I", self.frame_id)

        self.frame_raw_length = struct.pack("!B", self.frame_length)
        self.frame_raw_data = ''.join(struct.pack("!B", b) for b in self.frame_data)

    def parse_raw(self):

        if not self.frame_ext:
            self.frame_id = struct.unpack("!H", self.frame_raw_id)[0]
        else:
            self.frame_id = struct.unpack("!I", self.frame_raw_id)[0]

        self.frame_length = struct.unpack("!B", self.frame_raw_length)[0]
        self.frame_data = [struct.unpack("!B", x)[0] for x in self.frame_raw_data]


'''
Class to handle CAN messages and other data
'''


class CANSploitMessage:
    def __init__(self):  # Init EMPTY message

        self.debugText = ""
        self.CANFrame = None
        self.debugData = False
        self.CANData = False
        self.bus = 0
