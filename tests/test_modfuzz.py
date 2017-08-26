import time
import unittest

from cantoolz.engine import CANSploit


class ModFuzzTests(unittest.TestCase):

    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_fuzz_can(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_6.py")
        self.CANEngine.edit_module(0, {'id': [111], 'data': [0, 1], 'bytes': (0, 4), 'delay': 0})
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "s")
        time.sleep(3)
        ret = self.CANEngine.call_module(3, "p")
        print(ret)
        index = 3
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(16 == len(_bodyList[111]), "16 uiniq packets, should be sent")

    def test_fuzz_iso(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_6.py")
        self.CANEngine.edit_module(
            0,
            {
                'id': [[111, 112]],
                'data': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                'delay': 0,
                'index': [5, 18],
                'bytes': (0, 4),
                'mode': 'ISO'
            })
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "s")
        time.sleep(3)
        ret = self.CANEngine.call_module(3, "p")
        print(ret)
        index = 3
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(9 == len(_bodyList[111]), "9 uiniq packets, should be sent")
