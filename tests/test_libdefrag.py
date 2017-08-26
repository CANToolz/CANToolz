import time
import unittest

from cantoolz.engine import CANSploit


class LibDefragTests(unittest.TestCase):

    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_meta_add(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_5.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "l tests/data/replay.save")
        self.CANEngine.call_module(0, "r 0-21")
        time.sleep(2)
        mod_stat = 1
        ret = self.CANEngine.call_module(mod_stat, "a")
        print(ret)

        idx2 = ret.find("ID 0x7a6b and length 28")
        idx3 = ret.find("ID 0x7a6a and length 14")
        idx = ret.find("ID 0x7a6c and length 6")

        self.assertTrue(0 <= idx2, "Comment 'ID 31339' should be found ")
        self.assertTrue(0 <= idx3, "Comment 'ID 31338' should  be found ")
        self.assertFalse(0 <= idx, "Comment 'ID 31338' should NOT be found 3 times")
