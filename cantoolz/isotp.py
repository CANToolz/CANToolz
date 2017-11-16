from cantoolz.can import CANMessage


class ISOTPMessage:

    """
    dirty ISOTP impl
    ISO 15765-2

    https://en.wikipedia.org/wiki/ISO_15765-2
    """

    # Protocol Control Information
    #: int -- The frame is self-contained
    SINGLE_FRAME = 0
    #: int -- The frame is the first frame of a series of frames
    FIRST_FRAME = 1
    #: int -- The frame is the following frame after a first frame
    CONSECUTIVE_FRAME = 2
    #: int -- Acknowledge frame
    FLOW_CONTROL = 3

    def __init__(self, id=0, length=0, data=None, finished=False):
        """Initialize an empty ISO TP CAN message.

        :param int id: The CAN message ID
        :param int length: Length of the CAN message data
        :param list data: The CAN message data
        :param bool finished: True if there is no more data to add to the message. False otherwise.
        """
        self.message_id = id
        self.message_data = [] or data
        self.message_length = length
        self.message_finished = finished
        self._counterSize = 0
        self._seq = 0
        self._flow = -1
        self.padded = False

    @staticmethod
    def _get_padding(array):
        """Get the ISO TP padding from the CAN frames.

        :param list array: TODO

        :return: Padding of the ISO TP message.
        :rtype: int
        """
        array2 = array + []
        array2.reverse()
        cnt = 1
        std = array2[0]
        for x in array2[1:len(array2)]:
            if std == x:
                cnt += 1
            else:
                break
        return cnt

    # TODO: Use custom exception instead of int error codes
    def _add_frame_single(self, can):
        """Convert a CAN message into a single ISO TP frame.

        :param cantoolz.can.CANMessage: CAN Message to convert

        :return: Error code (>= 0 for success, < 0 otherwise)
        :rtype: int
        """
        length = can.frame_data[0] & 0x0F
        if not 0 < length < 8:
            return -1
        if can.frame_length != 8:
            if length + 1 == can.frame_length:
                self.message_data = can.frame_data[1:length + 1]
                self.message_length = length
                self.message_finished = True
                return 1
        else:
            padded = self._get_padding(can.frame_data)
            if padded > 0 and length + 1 == 8 - padded:
                self.message_data = can.frame_data[1:length + 1]
                self.message_length = length
                self.message_finished = True
                self.padded = True
                return 1
        return -7

    # TODO: Use custom exception instead of int error codes
    def _add_frame_first(self, can):
        """Convert a CAN message into the first frame of an ISO TP message.

        :param cantoolz.can.CANMessage: CAN Message to convert

        :return: Error code (>= 0 for success, < 0 otherwise)
        :rtype: int
        """
        length = can.frame_data[0] & 0x0F
        message_length = (length << 8) + can.frame_data[1]
        if message_length > 4095:
            return -6
        if self._counterSize == 0:
            self.message_length = message_length
            self._counterSize = 6
            self.message_data = can.frame_data[2:8]
            self._seq = 1  # Wait for first packet
            return 2
        return -2

    # TODO: Use custom exception instead of int error codes
    def _add_frame_consecutive(self, can):
        """Convert a CAN message into the consecutive frame of an ISO TP message.

        :param cantoolz.can.CANMessage: CAN Message to convert

        :return: Error code (>= 0 for success, < 0 otherwise)
        :rtype: int
        """
        length = can.frame_data[0] & 0x0F
        if length != self._seq:  # Wrong seq
            return -3

        _left = self.message_length - self._counterSize
        _add = min(_left, 7)
        self.message_data.extend(can.frame_data[1:_add + 1])
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

    # TODO: Use custom exception instead of int error codes
    def add_can(self, can):  # Init
        """Convert a CAN frame to the ISO TP format.

        :param cantoolz.can.CANMessage can: CAN message

        :return: Error code (>= 0 for success, < 0 otherwise)
        :rtype: int
        """
        ret = -5
        # The initial field is four bits indicating the frame type
        frame_type = (can.frame_data[0] & 0xF0) >> 4
        if frame_type == self.SINGLE_FRAME:
            ret = self._add_frame_single(can)
        elif frame_type == self.FIRST_FRAME:
            ret = self._add_frame_first(can)
        elif frame_type == self.CONSECUTIVE_FRAME and self._seq > 0:
            ret = self._add_frame_consecutive(can)
        elif frame_type == self.FLOW_CONTROL:
            ret = self._flow = can.frame_data[0] & 0x0F
        return ret

    @staticmethod
    def generate_can(fid, data, padding=None):  # generate CAN messages seq
        """Generate a CAN message in ISO TP format.

        :param int fid: CAN ID for the message
        :param list data: CAN message data
        :param int padding: Value of the padding, e.g. 0x00 (if padding is required)

        :return: List of cantoolz.can.CANMessage messages in ISO TP format representing the data.
        :rtype: list
        """
        _length = len(data)
        can_msg_list = []

        if _length < 8:
            padding_data = []
            padding_length = 0
            if padding is not None:
                padding_data = [int(padding)] * (7 - _length)
                padding_length = 8 - _length - 1
            can_msg_list.append(CANMessage.init_data(fid, _length + 1 + padding_length, [_length] + data[:_length] + padding_data))  # Single
        elif _length > 4095:
            return []
        else:
            can_msg_list.append(CANMessage.init_data(fid, 8, [(_length >> 8) + 0x10] + [_length & 0xFF] + data[:6]))
            seq = 1
            bytes = 6

            while bytes != _length:  # Rest
                sent = min(_length - bytes, 7)
                padding_data = []
                padding_length = 0
                if padding and sent < 7:
                    padding_data = [int(padding)] * (7 - sent)
                    padding_length = 8 - sent - 1
                can_msg_list.append(CANMessage.init_data(fid, 1 + sent + padding_length, [seq + 0x20] + data[bytes:bytes + sent] + padding_data))
                bytes += sent
                seq += 1
                if seq > 0xF:
                    seq = 0

        return can_msg_list
