import time

from ..utils import TestCANToolz


class TestTCP2CAN(TestCANToolz):

    def test_server(self):
        self.CANEngine.load_config("tests/configurations/conf_hw_tcp2can.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        # Replay CAN messages via replay.
        self.CANEngine.call_module(3, 'r')
        time.sleep(1)
        # Get status of analyze module.
        ret = self.CANEngine.call_module(6, 'S')
        print(ret)
        self.assertTrue(0 < ret.find("index: 0 sniffed: 12"), "Should be be 12 packets")
        # Replay CAN messages via replay~2.
        self.CANEngine.call_module(8, 'r')
        time.sleep(1)
        # Get status of analyze module.
        ret = self.CANEngine.call_module(1, 'S')
        print(ret)
        self.assertTrue(0 < ret.find("index: 0 sniffed: 24"), "Should be be 12 packets")
