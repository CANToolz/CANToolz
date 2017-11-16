import struct
import binascii
import bitstring

from cantoolz.module import CANModule


class CANMessage:

    """
    Generic class for CAN message.
    """

    DataFrame = 1
    RemoteFrame = 2
    ErrorFrame = 3
    OverloadFrame = 4

    def __init__(self, fid, length, data, extended, type):  # Init EMPTY message
        self.frame_id = min(0x1FFFFFFF, int(fid))  # Message ID
        self.frame_length = min(8, int(length))  # DATA length
        self.frame_data = list(data)[0:self.frame_length]  # DATA
        self.frame_ext = bool(extended)  # 29 bit message ID - boolean flag

        self.frame_type = type

    def __bytes__(self):
        return self.frame_raw_data

    def __len__(self):
        return self.frame_length

    def __int__(self):
        return self.frame_id

    def __str__(self):
        return hex(self.frame_id)

    def get_bits(self):
        fill = 8 - self.frame_length
        bits_array = '0b'
        bits_array += '0' * fill * 8
        for byte in self.frame_data:
            bits_array += bin(byte)[2:].zfill(8)
        return bitstring.BitArray(bits_array, length=64)

    def get_text(self):
        return hex(self.frame_id) + ":" + str(self.frame_length) + ":" + CANModule.get_hex(self.frame_raw_data)

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

    @frame_raw_data.setter
    def frame_raw_data(self, value):
        self.frame_data = list(value)[0:self.frame_length]  # DATA

    def to_hex(self):
        """CAN frame in HEX format ready to be sent (include ID, length and data)"""
        if not self.frame_ext:
            id = binascii.hexlify(struct.pack('!H', self.frame_id))[1:].zfill(3)
        else:
            id = binascii.hexlify(struct.pack('!I', self.frame_id)).zfill(8)
        length = binascii.hexlify(struct.pack('!B', self.frame_length))[1:].zfill(1)
        data = binascii.hexlify(bytes(self.frame_data)).zfill(self.frame_length * 2)
        return id + length + data

    @staticmethod
    def init_data(fid, length, data):  # Init
        if length > 8:
            length = 8
        if 0 <= fid <= 0x7FF:
            extended = False
        elif 0x7FF < fid <= 0x1FFFFFFF:
            extended = True
        else:
            fid = 0
            extended = False

        return CANMessage(fid, length, data, extended, 1)


class CANSploitMessage:

    """
    Class to handle CAN messages and other data.
    """

    def __init__(self):  # Init EMPTY message
        self.debugText = ""
        self.CANFrame = None
        self.debugData = False
        self.CANData = False
        self.bus = "Default"
