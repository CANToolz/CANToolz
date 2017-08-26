import time
import unittest

from cantoolz.engine import CANSploit


class ModGenPingEX(unittest.TestCase):

    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_ping_uds(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_5.py")
        self.CANEngine.edit_module(
            2,
            {
                'pipe': 2,
                'services': [
                    {"service": 1, "sub": [1, 2]},
                    {"service": [2, 3], "sub": 3},
                    {"service": "0x4-6", "sub": "0x4-6"}],
                'mode': 'UDS',
                'range': [1, 2]
            })
        time.sleep(1)
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(2, "s")
        time.sleep(1)
        mod_stat = 3
        ret1 = self.CANEngine.call_module(mod_stat, "p 0")
        print(ret1)
        self.assertTrue(0 <= ret1.find('020505'), "Should be found")
        self.assertTrue(0 <= ret1.find('020504'), "Should be found")
        self.assertTrue(0 <= ret1.find('020405'), "Should be found")
        self.assertTrue(0 <= ret1.find('020404'), "Should be found")
        self.assertTrue(0 <= ret1.find('020303'), "Should be found")
        self.assertTrue(0 <= ret1.find('020203'), "Should be found")
        self.assertTrue(0 <= ret1.find(' 020102 '), "Should be found")
        self.assertTrue(0 <= ret1.find(' 020101 '), "Should be found")
        self.assertFalse(0 <= ret1.find(' 0101 '), "Should not be found")

    # https://github.com/eik00d/CANToolz/issues/93 by @DePierre
    def test_ping_uds_none_crash(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/test_5.py")
        self.CANEngine.edit_module(
            2,
            {
                'pipe': 2,
                'services': [
                    {"service": 1, "sub": None}],
                'mode': 'UDS',
                'range': [1, 2]
            })
        time.sleep(1)

        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(2, "s")
        time.sleep(1)
        mod_stat = 3
        ret1 = self.CANEngine.call_module(mod_stat, "p 0")
        print(ret1)
        self.assertTrue(0 <= ret1.find('0x1'), "Should be found")
        self.assertTrue(0 <= ret1.find('0101'), "Should be found")

