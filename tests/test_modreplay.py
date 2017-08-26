import time
import unittest

from cantoolz.engine import CANSploit


class ModReplayTests(unittest.TestCase):

    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_replay1(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_3.py")
        self.CANEngine.start_loop()
        time.sleep(2)
        self.CANEngine.call_module(2, "s")
        num = self.CANEngine.call_module(1, "p")
        self.assertTrue(0 <= num.find("Loaded packets: 0"), "Should be be 0 packets")
        time.sleep(3)
        self.CANEngine.call_module(1, "g")
        #time.sleep(1)
        self.CANEngine.call_module(0, "t 4:8:1122334411111111")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 4:8:1122334411111111")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 666:8:1122334411111111")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 5:8:1122334411111111")
        time.sleep(3)
        num = self.CANEngine.call_module(1, "p")

        #print("num is " + num)
        self.assertTrue(0 <= num.find("Loaded packets: 4"), "Should be be 4 packets")
        self.CANEngine.call_module(1, "g")
        ret = self.CANEngine.call_module(1, "d 0-4")
        time.sleep(1)
        print(ret)
        self.CANEngine.call_module(2, "s")
        time.sleep(1)
        self.CANEngine.call_module(1, "r 0-4")
        time.sleep(5)
        self.CANEngine.call_module(1, "c")
        time.sleep(1)
        num = self.CANEngine.call_module(1, "p")
        time.sleep(1)
        self.assertTrue(0 <= num.find("Loaded packets: 0"), "Should be be 0 packets")
        index = 2
        ret = self.CANEngine.call_module(2, "p")
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        print(ret)
        time.sleep(1)
        self.assertTrue(len(_bodyList) == 3, "Should be be 3 groups found")

    def test_replay2(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_4.py")
        self.CANEngine.start_loop()
        num = self.CANEngine.call_module(1, "p")
        time.sleep(1)
        self.assertTrue(0 <= num.find("Loaded packets: 4"), "Should be be 4 packets")
        index = 2
        self.CANEngine.call_module(2, "p")
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(len(_bodyList) == 0, "Should be 0 packets sent")
        self.CANEngine.call_module(1, "r 2-4")
        time.sleep(3)

        ret = self.CANEngine.call_module(2, "p")
        print(ret)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList

        self.assertTrue(2 == len(_bodyList), "Should be 2 packets sent")
        self.assertTrue(666 in _bodyList, "ID 666 should be dound")
        self.assertTrue(5 in _bodyList, "ID 5 should be found")
        self.assertFalse(4 in _bodyList, "ID 4 should not be found ")
        self.CANEngine.call_module(2, "r tests/data/new.save")
        self.CANEngine.call_module(1, "l tests/data/new.save")
        ret = self.CANEngine.call_module(1, "p")
        print(ret)
        self.assertTrue(0 <= ret.find("Loaded packets: 6"), "Should be 26packets")
        self.CANEngine.call_module(1, "c")
        self.CANEngine.call_module(1, "l tests/data/new.save")
        ret = self.CANEngine.call_module(1, "p")
        print(ret)
        self.assertTrue(0 <= ret.find("Loaded packets: 2"), "Should be 2 packets")
