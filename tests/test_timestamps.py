import time
import unittest

from cantoolz.engine import CANSploit


class TimeStampz(unittest.TestCase):

    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_timestamp(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_11.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        num = self.CANEngine.call_module(0, "p")
        self.assertTrue(0 <= num.find("Loaded packets: 11"), "Should be be 11 packets")
        time1 = time.clock()
        self.CANEngine.call_module(0, "r")
        while self.CANEngine._enabledList[0][1]._status < 100.0:
            continue
        ret = self.CANEngine.call_module(1, "p")
        time2 = time.clock()

        print("TIME: " + str(time2 - time1))

        st = self.CANEngine.call_module(1, "S")
        print(st)
        self.assertTrue(0 <= st.find("Sniffed frames (overall): 11"), "Should be be 11 packets")
        self.CANEngine.call_module(1, "r tests/data/format.dump")
        self.assertTrue(13.99 < time2 - time1 < 15.99, "Should be around 14 seconds")
        self.CANEngine.stop_loop()
        self.CANEngine = None

        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_12.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        num = self.CANEngine.call_module(0, "p")
        self.assertTrue(0 <= num.find("Loaded packets: 11"), "Should be be 11 packets")
        time1 = time.clock()
        self.CANEngine.call_module(0, "r")
        while self.CANEngine._enabledList[0][1]._status < 100.0:
            continue
        ret = self.CANEngine.call_module(1, "p")
        print(ret)
        time2 = time.clock()
        print("TIME: " + str(time2 - time1))
        self.assertTrue(13.99 < time2 - time1 < 15.99, "Should be around 14 seconds")
        st = self.CANEngine.call_module(1, "S")
        self.assertTrue(0 <= st.find("Sniffed frames (overall): 11"), "Should be be 11 packets")
