import time

from ..utils import TestCANToolz


class TestSimpleIO(TestCANToolz):

    def test_send_recieve(self):
        self.CANEngine.load_config('tests/configurations/conf_simple_io.py')
        self.CANEngine.start_loop()
        analyze = self.CANEngine.find_module('analyze')
        simple_io = self.CANEngine.find_module('simple_io')
        time.sleep(1)
        # Write CAN messages via SimpleIO.
        self.CANEngine.call_module(simple_io, 'w 0x111:3:001122')
        self.CANEngine.call_module(simple_io, 'w 111:4:00112233')
        self.CANEngine.call_module(simple_io, 'w 0x111:0011223344')
        time.sleep(1)
        # Print table of sniffed CAN packets from analyze.
        ret = self.CANEngine.call_module(analyze, 'p')
        self.assertTrue(ret.find(" 001122 ") > 0, "Should be found")
        self.assertTrue(ret.find(" 00112233 ") > 0, "Should be found")
        self.assertTrue(ret.find(" 0011223344 ") > 0, "Should be found")
        self.assertTrue(ret.find(" 0x111 ") > 0, "Should be found")
        self.assertTrue(ret.find(" 0x6f ") > 0, "Should be found")
        print(ret)
        # Read CAN messages via SimpleIO.
        ret1 = self.CANEngine.call_module(simple_io, 'r')
        ret2 = self.CANEngine.call_module(simple_io, 'r')
        ret3 = self.CANEngine.call_module(simple_io, 'r')
        print(ret1)
        print(ret2)
        print(ret3)
        self.assertTrue(ret1.find("0x111:3:001122") >= 0, "Should be found")
        self.assertTrue(ret2.find("0x6f:4:00112233") >= 0, "Should be found")
        self.assertTrue(ret3.find("0x111:5:0011223344") >= 0, "Should be found")

