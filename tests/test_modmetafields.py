import time
import unittest

from cantoolz.engine import CANSploit


class ModMetaFields(unittest.TestCase):

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
        self.CANEngine.call_module(mod_stat, "bits 1,8,  hex:16:COUNTER, ascii:56:TEXT")
        ret1 = self.CANEngine.call_module(mod_stat, "p 0")
        print(ret1)
        self.assertTrue(0 <= ret1.find('Default    0x1    8         COUNTER: 1122 TEXT: 3DUfw'), "Should be found")
        self.assertTrue(0 <= ret1.find('Default    0x1    8         COUNTER: 3322 TEXT: 3DUfw'), "Should be found")
        self.assertTrue(0 <= ret1.find('Default    0x1    8         COUNTER: 3322 TEXT: 3DUfw'), "Should be found")
