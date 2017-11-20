import unittest
import struct
import bitstring

from cantoolz.can import CAN


class TestCan(unittest.TestCase):

    def test_init(self):
        # Init CAN without any parameters
        can = CAN()
        self.assertTrue(can.id == 0 and can.length is None and can.data is None and can.mode == CAN.STANDARD and can.type == CAN.DATA and can.bus == 'Default' and can.debug == None)
        # Standard
        can = CAN(id=1, length=1, data=[1])
        self.assertTrue(can.id == 1 and can.length == 1 and can.data == [1] and can.mode == CAN.STANDARD and can.type == CAN.DATA and can.bus == 'Default' and can.debug == None)
        # Extended
        can = CAN(id=1, length=1, data=[1], mode=CAN.EXTENDED)
        self.assertTrue(can.id == 1 and can.length == 1 and can.data == [1] and can.mode == CAN.EXTENDED)
        can = CAN(id=0x800, length=1, data=[1])
        self.assertTrue(can.id == 0x800 and can.length == 1 and can.data == [1] and can.mode == CAN.EXTENDED and can.type == CAN.DATA and can.bus == 'Default' and can.debug == None)

    def test_attributes(self):
        can = CAN()
        can.id = 1
        self.assertTrue(can.id == 1 and can.mode == CAN.STANDARD)
        can = CAN()
        can.id = 1
        can.mode = CAN.EXTENDED
        self.assertTrue(can.id == 1 and can.mode == CAN.EXTENDED)
        can = CAN()
        can.id = 0x800
        self.assertTrue(can.id == 0x800 and can.mode == CAN.EXTENDED)
        can = CAN()
        can.id = 0x10000
        can.mode = CAN.STANDARD
        with self.assertRaises(struct.error):
            _ = can.raw_id

    def test_remote(self):
        can = CAN(id=1, length=1, data=[1], type=CAN.REMOTE)
        self.assertTrue(can.type == CAN.REMOTE and can.data == [] and can.length == 1)
        can = CAN(id=1, length=1, data=[1])
        can.type = CAN.REMOTE
        self.assertTrue(can.type == CAN.REMOTE and can.data == [] and can.length == 1)

    def test_raw_attributes(self):
        can = CAN(data=[1])
        self.assertTrue(can.data == [1] and can.raw_data == b'\x01')
        can = CAN(id=2, mode=CAN.STANDARD)
        self.assertTrue(can.id == 2 and can.raw_id == b'\x00\x02')
        can = CAN(id=2, mode=CAN.EXTENDED)
        self.assertTrue(can.id == 2 and can.raw_id == b'\x00\x00\x00\x02')
        can = CAN(length=3)
        self.assertTrue(can.length == 3 and can.raw_length == b'\x03')
        can = CAN(id=1, length=1, data=[1])
        self.assertTrue(can.raw == b'\x00\x01\x01\x01')
        can = CAN(id=1, length=1, type=CAN.REMOTE)
        self.assertTrue(can.raw == b'\x00\x01\x01')

    def test_transformation(self):
        can = CAN(id=1, length=2, data=[3, 4])
        self.assertTrue(int(can) == 1 and bytes(can) == b'\x03\x04' and str(can) == '0x1:2:0304' and repr(can) == '<CAN(id=1, length=2, data=[3, 4])>')

    def test_bits(self):
        can = CAN(id=1, length=3, data=[3, 1, 2])
        self.assertTrue(can.bits == bitstring.BitArray('0b0000000000000000000000000000000000000000000000110000000100000010', length=64))

    def test_truncated_data(self):
        can = CAN(id=1, length=0, data=[1, 2, 3])
        self.assertTrue(can.data == [])
        can = CAN(id=1, length=1, data=[1, 2, 3])
        self.assertTrue(can.data == [1])
        can = CAN(id=1, length=2, data=[1, 2, 3])
        self.assertTrue(can.data == [1, 2])
        can = CAN(id=1, length=3, data=[1, 2, 3])
        self.assertTrue(can.data == [1, 2, 3])
        can = CAN(id=1, length=4, data=[1, 2, 3])
        self.assertTrue(can.data == [1, 2, 3])
