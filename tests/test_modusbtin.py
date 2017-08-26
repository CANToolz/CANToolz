import time
import unittest

from cantoolz.engine import CANSploit


class ModUsbTin(unittest.TestCase):

    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_usbtin(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_7.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(1, "r")
        self.CANEngine.call_module(3, "t T112233446112233445566")
        time.sleep(1)
        ret = self.CANEngine.call_module(2, "p")
        _bodyList = self.CANEngine._enabledList[2][1]._bodyList
        self.assertTrue(6 == len(_bodyList), "6 uiniq ID, should be sent")
        self.assertTrue(0 <= ret.find(" 0x2bc "), "Message should be in the list")
        self.assertTrue(0 <= ret.find(" 2f410d0011223344 "), "Message should be in the list")
        self.assertTrue(0 <= ret.find(" 112233445566"), "Message should be in the list")
        self.assertTrue(0 <= ret.find(" 0x11223344 "), "Message should be in the list")

