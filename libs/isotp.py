from libs.can import *

'''
dirty ISOTP impl
ISO 15765-2

https://en.wikipedia.org/wiki/ISO_15765-2
'''


class ISOTPMessage:
    # PCI
    SingleFrame = 0
    FirstFrame = 1
    ConsecutiveFrame = 2
    FlowControl = 3

    ClearToSend = 10
    Wait = 11
    OverflowAbort = 12

    def __init__(self, id = 0, length = 0, data = [], finished = False):  # Init EMPTY message
        self.message_id = id
        self.message_data = data
        self.message_length = length
        self.message_finished = finished
        self._counterSize = 0
        self._seq = 0
        self._flow = -1

    def add_can(self, can_msg):  # Init
        # The initial field is four bits indicating the frame type,
        pciType = (can_msg.frame_data[0] & 0xF0) >> 4
        sz = (can_msg.frame_data[0] & 0x0F)

        if pciType == self.SingleFrame:  # Single frame
            if 0 < sz < 8:
                if sz + 1 == can_msg.frame_length:
                    self.message_data = can_msg.frame_data[1:sz + 1]
                    self.message_length = sz
                    self.message_finished = True
                    return 1
                return -7
            else:
                return -1
        elif pciType == self.FirstFrame:  # First frame
            message_length = (sz << 8) + can_msg.frame_data[1]
            if message_length > 4095:
                return -6
            if self._counterSize == 0:
                self.message_length = message_length
                self._counterSize = 6
                self.message_data = can_msg.frame_data[2:8]
                self._seq = 1  # Wait for first packet
                return 2
            else:
                return -2
        elif pciType == self.ConsecutiveFrame and self._seq > 0:  # All next frames until last one
            if sz != self._seq:  # Wrong seq
                return -3
            _left = self.message_length - self._counterSize
            _add = min(_left, 7)
            self.message_data.extend(can_msg.frame_data[1:_add + 1])

            self._counterSize += _add

            if self._counterSize == self.message_length:
                self.message_finished = True
                return 1
            elif self._counterSize > self.message_length:
                return -4

            self._seq += 1

            if self._seq > 0xF:
                self._seq = 0

            return 2

        elif pciType == self.FlowControl:
            self._flow = sz
            return -9
        else:
            return -5

    @classmethod
    def generate_can(self, fid, data):  # generate CAN messages seq
        _length = len(data)
        can_msg_list = []

        if _length < 8:
            can_msg_list.append(CANMessage.init_data(fid, _length + 1, [_length] + data[:_length]))  # Single
        elif _length > 4095:
            return []
        else:
            can_msg_list.append(CANMessage.init_data(fid, 8, [(_length >> 8) + 0x10] + [_length & 0xFF] + data[:6]))
            seq = 1
            bytes = 6

            while bytes != _length:  # Rest
                sent = min(_length - bytes, 7)
                can_msg_list.append(CANMessage.init_data(fid, 1 + sent, [seq + 0x20] + data[bytes:bytes + sent]))
                bytes += sent
                seq += 1
                if seq > 0xF:
                    seq = 0

        return can_msg_list
