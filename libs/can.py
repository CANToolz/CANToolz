import struct
import collections

'''
Generic class for CAN message
'''


class CANMessage:
    DataFrame = 1
    RemoteFrame = 2
    ErrorFrame = 3
    OverloadFrame = 4

    def __init__(self, fid, length, data, extended, type):  # Init EMPTY message
        self.frame_id = int(fid)  # Message ID
        self.frame_length = int(length)  # DATA length
        self.frame_data = list(data)  # DATA
        self.frame_ext = bool(extended)  # 29 bit message ID - boolean flag

        self.frame_type = type


    @property
    def frame_raw_id(self):
        if not self.frame_ext:
            return struct.pack("!H", self.frame_id)
        else:
            return struct.pack("!I", self.frame_id)

    @property
    def frame_raw_length(self):
        return struct.pack("!B", self.frame_length)

    @property
    def frame_raw_data(self):
        return bytes(self.frame_data)


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

'''
Class to handle CAN messages and other data
'''


class CANSploitMessage:
    def __init__(self):  # Init EMPTY message

        self.debugText = ""
        self.CANFrame = None
        self.debugData = False
        self.CANData = False
        self.bus = "Default"
