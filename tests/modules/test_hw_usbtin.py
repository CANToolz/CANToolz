import time

from ..utils import TestCANToolz


class TestUSBtin(TestCANToolz):

    def test_usbtin(self):
        self.CANEngine.load_config("tests/configurations/conf_hw_usbtin.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        # Replay loaded CAN messages via replay
        self.CANEngine.call_module(1, 'r')
        # Send CAN message via hw_USBtin
        self.CANEngine.call_module(3, 't T112233446112233445566')
        time.sleep(1)
        # Print table of sniffed CAN packets from analyze.
        ret = self.CANEngine.call_module(2, 'p')
        _bodyList = self.CANEngine.actions[2][1]._bodyList
        self.assertTrue(6 == len(_bodyList), "6 unique ID, should be sent")
        self.assertTrue(0 <= ret.find(" 0x2bc "), "Message should be in the list")
        self.assertTrue(0 <= ret.find(" 2f410d0011223344 "), "Message should be in the list")
        self.assertTrue(0 <= ret.find(" 112233445566"), "Message should be in the list")
        self.assertTrue(0 <= ret.find(" 0x11223344 "), "Message should be in the list")
