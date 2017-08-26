import time
import unittest

from cantoolz.engine import CANSploit


class TCP2CAN(unittest.TestCase):

    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_server(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_13.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(3, "r ")
        time.sleep(1)
        ret = self.CANEngine.call_module(6, "S ")
        print(ret)
        self.assertTrue(0 < ret.find("index: 0 sniffed: 12"), "Should be be 12 packets")
        self.CANEngine.call_module(8, "r ")
        time.sleep(1)
        ret = self.CANEngine.call_module(1, "S ")
        print(ret)
        self.assertTrue(0 < ret.find("index: 0 sniffed: 24"), "Should be be 12 packets")
