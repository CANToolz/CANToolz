import time
import unittest

from cantoolz.engine import CANSploit


class ModStatMetaTests(unittest.TestCase):

    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_meta_add(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_5.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "r 0-9")
        time.sleep(2)
        mod_stat = 1
        #self.CANEngine.call_module(mod_stat, "i 1800, .*13039313439, TEST_UDS2")
        self.CANEngine.call_module(mod_stat, "i 0x708 ,.*, TEST UDS")
        self.CANEngine.call_module(mod_stat, "i 0x2bc , 0f410d00 , TEST 700")
        self.CANEngine.call_module(mod_stat, "i 1803 , 2f............44 , TEST 1803")
        self.CANEngine.call_module(mod_stat, "i 1801 , 036f , TEST 1801")

        self.CANEngine.call_module(mod_stat, "z tests/data/meta.txt")
        ret = self.CANEngine.call_module(mod_stat, "p")
        print(ret)
        idx = ret.find("TEST UDS")
        self.assertTrue(0 <= idx, "Comment 'TEST UDS' should be found 1 times")
        idx2 = ret.find("TEST UDS", idx + 8)
        self.assertTrue(0 <= idx2, "Comment 'TEST UDS' should be found 2 times")
        #idx3 = ret.find("TEST_UDS2", idx2 + 8)
        self.assertTrue(0 <= ret.find("TEST 700"), "Comment 'TEST 700' should be found 1 times")
        self.assertTrue(0 <= ret.find("TEST 1803"), "Comment 'TEST 1803' should be found 1 times")
        self.assertFalse(0 <= ret.find("TEST 1801"), "Comment 'TEST 1801' should NOT be found 1 times")

    def test_meta_add2(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_5.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "r 0-9")
        time.sleep(2)
        mod_stat = 1
        ret = self.CANEngine.call_module(mod_stat, "p")
        idx = ret.find("TEST UDS")
        self.assertTrue(-1 == idx, "Comment 'TEST UDS' should NOT be found")
        self.CANEngine.call_module(mod_stat, "l tests/data/meta.txt")
        ret = self.CANEngine.call_module(mod_stat, "p")
        print(ret)
        self.CANEngine.call_module(mod_stat, "d tests/data/meta_test.csv")
        idx = ret.find("TEST UDS")
        self.assertTrue(0 <= idx, "Comment 'TEST UDS' should be found 1 times")
        idx2 = ret.find("TEST UDS", idx + 8)
        self.assertTrue(0 <= idx2, "Comment 'TEST UDS' should be found 2 times")
        #idx3 = ret.find("TEST_UDS2", idx2 + 8)
        #self.assertTrue(0 <= idx3, "Comment 'TEST UDS' should be found 3 times")
        self.assertTrue(0 <= ret.find("TEST 700"), "Comment 'TEST 700' should be found 1 times")
        self.assertTrue(0 <= ret.find("TEST 1803"), "Comment 'TEST 1803' should be found 1 times")
        self.assertFalse(0 <= ret.find("TEST 1801"), "Comment 'TEST 1801' should NOT be found 1 times")
