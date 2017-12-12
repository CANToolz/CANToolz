import struct
import bitstring


class CAN:

    """Class representing a CAN frame on the bus."""

    # CAN frame mode, from standard to remote extended CAN frame.
    #: Standard CAN frame with 11-bit ID
    STANDARD = 0x00
    #: Extended CAN frame with 29-bit ID
    EXTENDED = 0x01
    # CAN frame type, from data to overload CAN frame.
    #: Data CAN frame
    DATA = 0x10
    #: Remote CAN frame
    REMOTE = 0x20
    #: Error CAN frame
    ERROR = 0x30
    #: Overload CAN frame
    OVERLOAD = 0x40

    def __init__(self, id=0, length=None, data=None, mode=STANDARD, type=DATA, bus='Default', debug=None):
        """Initialize a CAN frame.

        :param int id: ID of the CAN frame (from 0 to 0x1FFFFFFF).
        :param int length: Length of the data in the CAN frame (from 0 to 8).
        :param list data: CAN data in the frame (from 0 to 8 elements).
        :param int mode: CAN frame mode (STANDARD or EXTENDED).
        :param int type: CAN frame type (DATA, REMOTE, ERROR or OVERLOAD).
        :param str bus: CAN bus where the frame comes from/goes to.
        :param dict debug: Debug message in case of debug frame.
        """
        self._id = 0
        self._length = None
        self._data = None
        self._mode = self.STANDARD
        self._type = self.DATA
        self.bus = ''
        self.debug = None
        self.init(id=id, length=length, data=data, mode=mode, type=type, bus=bus, debug=debug)

    def __len__(self):
        if self._length is None:
            return 0
        return self._length

    def __int__(self):
        return self._id

    def __repr__(self):
        return '<CAN(id={}, length={}, data={})>'.format(self._id, self._length, self._data)

    def __str__(self):
        if self._data is None:
            return '{}:{}:{}'.format(hex(self._id), self._length, self._data)
        return '{}:{}:{}'.format(hex(self._id), self._length, self.raw_data.hex())

    def __bytes__(self):
        if self._data is None:
            return b''
        return bytes(self._data)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if 0 <= value <= 0x7FF:
            self._id = value
            if self._mode is not self.EXTENDED:
                self._mode = self.STANDARD
        elif 0x7FF < value <= 0x1FFFFFFF:
            self._id = value
            self._mode = self.EXTENDED
        else:
            raise ValueError("Invalid CAN frame ID '{}'. Must be >= 0 and <= 0x1FFFFFFF".format(value))

    @property
    def raw_id(self):
        if self._mode == self.STANDARD:
            return struct.pack('!H', self._id)  # 2-byte ID
        return struct.pack('!I', self._id)  # 4-byte ID

    @property
    def data(self):
        if self._data is None:
            return None
        length = self._length
        if length is None:
            length = len(self._data)
        return self._data[:length]

    @data.setter
    def data(self, value):
        if value is not None:
            if isinstance(value, (str, bytes)):
                value = list(value)
            if not isinstance(value, list):
                raise TypeError("Invalid CAN frame data '{}'. Must be of type list or None".format(value))
        self._data = value

    @property
    def raw_data(self):
        if self._data is None:
            return None
        length = self._length
        if length is None:
            length = len(self._data)
        return bytes(self._data[:length])

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value):
        self._length = min(max(0, value), 8)

    @property
    def raw_length(self):
        return struct.pack('!B', self._length)

    @property
    def raw(self):
        """"Representation of CAN data in bytes.

        :return: Bytes representing the CAN frame (id + length + data)
        :rtype: bytes
        """
        if self._data is None:
            return self.raw_id + self.raw_length
        return self.raw_id + self.raw_length + self.raw_data

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value == self.STANDARD or value == self.EXTENDED:
            self._mode = value
        else:
            raise ValueError("Invalid CAN frame mode '{}'. Must be STANDARD or EXTENDED.".format(value))

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value in [self.DATA, self.REMOTE, self.ERROR, self.OVERLOAD]:
            self._type = value
            if value == self.REMOTE:
                self._data = []
        else:
            raise ValueError("Invalid CAN frame type '{}'. Must be DATA, REMOTE, ERROR or OVERLOAD.".format(value))

    @property
    def bits(self):
        """"Representation of CAN data in bits.

        :return: Bits representation of CAN data
        :rtype: bitstring.BitArray
        """
        fill = 8 - self._length
        bits_array = '0b' + '0' * fill * 8
        for byte in self._data:
            bits_array += bin(byte)[2:].zfill(8)
        return bitstring.BitArray(bits_array, length=64)

    def init(self, **kwargs):
        """Re-initialize the CAN class attributes.

        :param int id: ID of the CAN frame (from 0 to 0x1FFFFFFF).
        :param int length: Length of the data in the CAN frame (from 0 to 8).
        :param list data: CAN data in the frame (from 0 to 8 elements).
        :param int mode: CAN frame mode (STANDARD or EXTENDED).
        :param int type: CAN frame type (DATA, REMOTE, ERROR or OVERLOAD).
        :param str bus: CAN bus where the frame comes from/goes to.
        :param str debug: Debug message in case of debug frame.

        :raises AttributeError: When the attribute is not known.
        """
        # Order matters:
        # - CAN.id updated last to force CAN.mode to be updated.
        # - CAN.type updated last to force CAN.data to be updated.
        id = kwargs.pop('id', None)
        type = kwargs.pop('type', None)
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)
        if id is not None:
            setattr(self, 'id', id)
        if type is not None:
            setattr(self, 'type', type)
