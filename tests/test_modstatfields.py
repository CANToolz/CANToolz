import time
import unittest

from cantoolz.engine import CANSploit


class ModStatFields(unittest.TestCase):

    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_fields(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_5.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "c")
        time.sleep(1)
        self.CANEngine.call_module(0, "l tests/data/test_fields.dump")
        time.sleep(1)
        self.CANEngine.call_module(0, "r")
        time.sleep(1)
        mod_stat = 1
        ret1 = self.CANEngine.call_module(mod_stat, "show")
        ret2 = self.CANEngine.call_module(mod_stat, "fields 2, hex")
        print(ret1)
        self.assertTrue(0 <= ret1.find("ECU: 0x2     Length: 2     FIELDS DETECTED: 2"), "Should be found")
        self.assertTrue(0 <= ret1.find("ECU: 0x1     Length: 7     FIELDS DETECTED: 2"), "Should be found")
        self.assertTrue(0 <= ret1.find("ECU: 0x1     Length: 8     FIELDS DETECTED: 3"), "Should be found")
        print(ret2)
        self.assertTrue(0 <= ret2.find("1111    0"), "Should be found")
        self.assertTrue(0 <= ret2.find("1110    0"), "Should be found")

        ret2 = self.CANEngine.call_module(mod_stat, "fields 2, bin")
        print(ret2)
        self.assertTrue(0 <= ret2.find("1000100010001    000"), "Should be found")
        self.assertTrue(0 <= ret2.find("1000100010000    001"), "Should be found")

        ret2 = self.CANEngine.call_module(mod_stat, "fields 1, int")

        self.assertTrue(0 <= ret2.find("1    1    9626517791733640"), "Should be found")
        self.assertTrue(0 <= ret2.find("2    2    9626517791733640"), "Should be found")
        self.assertTrue(0 <= ret2.find("3    3    9626517791733640"), "Should be found")
        self.assertTrue(0 <= ret2.find("17895699    17895697"), "Should be found")
        self.assertTrue(0 <= ret2.find("17895697    17895697"), "Should be found")
