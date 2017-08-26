import time
import unittest

from cantoolz.engine import CANSploit


class ModStatTests(unittest.TestCase):

    def tearDown(self):
        self.CANEngine.stop_loop()

    def test_stat(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config('tests/configurations/test_1.py')
        self.CANEngine.edit_module(1, {'pipe': 2})
        time.sleep(1)
        self.CANEngine.start_loop()
        self.CANEngine.call_module(0, "t 4:4:11223344")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 4:4:11223344")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 4:8:1122334411111111")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 1:4:11223344")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 455678:8:1122334411223344")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 4:4:1122334455")
        time.sleep(1)
        index = 1

        ret = self.CANEngine.call_module(1, "p")
        print(ret)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList

        self.assertTrue(4 in _bodyList, "We should be able to find ID 4")
        self.assertTrue(455678 in _bodyList, "We should be able to find ID 455678")
        self.assertFalse(2 in _bodyList, "We should not be able to find ID 2")
        self.assertFalse(0 in _bodyList, "We should not be able to find ID 0")

        self.CANEngine.call_module(1, "c")
        self.CANEngine.call_module(0, "t 2:8:1122334411223344")
        time.sleep(1)
        self.CANEngine.call_module(1, "p")
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertFalse(4 in _bodyList, "We should not be able to find ID 4")
        self.assertFalse(455678 in _bodyList, "We should not be able to find ID 455678")
        self.assertTrue(2 in _bodyList, "We should be able to find ID 2")
