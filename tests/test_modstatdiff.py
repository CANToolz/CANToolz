import time
import unittest

from cantoolz.engine import CANSploit


class ModStatDiffTests(unittest.TestCase):

    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_diff(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_5.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "r 0-3")
        time.sleep(1)
        self.CANEngine.call_module(1, "D")
        time.sleep(1)
        self.CANEngine.call_module(0, "r 0-3")
        time.sleep(1)
        ret = self.CANEngine.call_module(1, "I")
        self.assertFalse(0 <= ret.find(" 0x707 "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x2bc "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x70b "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x709 "), "Should be empty diff")
        self.CANEngine.call_module(0, "r 0-6")
        time.sleep(1)

        ret = self.CANEngine.call_module(1, "I")
        print(ret)
        self.assertTrue(0 <= ret.find(" 0x707 "), "Should be empty diff")
        self.assertTrue(0 <= ret.find(" 0x708 "), "Should be empty diff")
        self.assertTrue(0 <= ret.find("03410d00"), "Should not be empty diff")
        self.assertTrue(0 <= ret.find("1014490201314731"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find(" 0x2bc "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x70b "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x709 "), "Should be empty diff")

        self.CANEngine.call_module(0, "r 0-6")
        time.sleep(1)
        ret = self.CANEngine.call_module(1, "N ")
        print(ret)
        self.assertTrue(0 <= ret.find(" 0x707 "), "Should be empty diff")
        self.assertTrue(0 <= ret.find(" 0x708 "), "Should be empty diff")
        self.assertTrue(0 <= ret.find("03410d00"), "Should not be empty diff")
        self.assertTrue(0 <= ret.find("1014490201314731"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find(" 0x2bc "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x70b "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x709 "), "Should be empty diff")

        self.CANEngine.call_module(1, "D , TEST BUFF")
        self.CANEngine.call_module(0, "r 0-6")
        time.sleep(1)
        self.CANEngine.call_module(1, "D , TEST BUFF2")
        self.CANEngine.call_module(0, "r")
        time.sleep(1)
        ret = self.CANEngine.call_module(1, "I 2,3")
        self.assertFalse(0 <= ret.find(" 0x707 "), "Should be empty diff")
        self.assertTrue(0 <= ret.find(" 0x708 "), "Should be empty diff")
        self.assertFalse(0 <= ret.find("03410d00"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find("1014490201314731"), "Should be empty diff")
        self.assertTrue(0 <= ret.find("215a543533383236"), "Should not be empty diff")
        self.assertTrue(0 <= ret.find("2246313039313439"), "Should not be empty diff")

        ret = self.CANEngine.call_module(1, "I 2,3,2")
        self.assertFalse(0 <= ret.find(" 0x707 "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x708 "), "Should be empty diff")
        self.assertFalse(0 <= ret.find("03410d00"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find("1014490201314731"), "Should be empty diff")
        self.assertFalse(0 <= ret.find("215a543533383236"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find("2246313039313439"), "Should not be empty diff")

        ret = self.CANEngine.call_module(1, "I 2,3,3")
        self.assertFalse(0 <= ret.find(" 0x707 "), "Should be empty diff")
        self.assertTrue(0 <= ret.find(" 0x708 "), "Should be empty diff")
        self.assertFalse(0 <= ret.find("03410d00"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find("1014490201314731"), "Should be empty diff")
        self.assertTrue(0 <= ret.find("215a543533383236"), "Should not be empty diff")
        self.assertTrue(0 <= ret.find("2246313039313439"), "Should not be empty diff")

        ret = self.CANEngine.call_module(1, "N")
        self.assertFalse(0 <= ret.find(" 0x707 "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x708 "), "Should be empty diff")
        self.assertFalse(0 <= ret.find("03410d00"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find("1014490201314731"), "Should be empty diff")
        self.assertFalse(0 <= ret.find("215a543533383236"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find("2246313039313439"), "Should not be empty diff")
