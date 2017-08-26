import time
import unittest

from cantoolz.engine import CANSploit


class SimpleIO(unittest.TestCase):

    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_send_recieve(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_10.py")
        self.CANEngine.start_loop()
        mod_stat = self.CANEngine.find_module('mod_stat')
        simple_io = self.CANEngine.find_module('simple_io')
        time.sleep(1)
        self.CANEngine.call_module(simple_io, "w 0x111:3:001122")
        self.CANEngine.call_module(simple_io, "w 111:4:00112233")
        self.CANEngine.call_module(simple_io, "w 0x111:0011223344")
        time.sleep(1)
        ret = self.CANEngine.call_module(mod_stat, "p")
        self.assertTrue(ret.find(" 001122 ") > 0, "Should be found")
        self.assertTrue(ret.find(" 00112233 ") > 0, "Should be found")
        self.assertTrue(ret.find(" 0011223344 ") > 0, "Should be found")
        self.assertTrue(ret.find(" 0x111 ") > 0, "Should be found")
        self.assertTrue(ret.find(" 0x6f ") > 0, "Should be found")
        print(ret)
        ret1 = self.CANEngine.call_module(simple_io, "r")
        ret2 = self.CANEngine.call_module(simple_io, "r")
        ret3 = self.CANEngine.call_module(simple_io, "r")
        print(ret1)
        print(ret2)
        print(ret3)
        self.assertTrue(ret1.find("0x111:3:001122") >= 0, "Should be found")
        self.assertTrue(ret2.find("0x6f:4:00112233") >= 0, "Should be found")
        self.assertTrue(ret3.find("0x111:5:0011223344") >= 0, "Should be found")
