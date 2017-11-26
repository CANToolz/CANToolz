import unittest

from cantoolz.engine import CANSploit


class TestCANToolz(unittest.TestCase):

    def setUp(self):
        self.CANEngine = CANSploit()

    def tearDown(self):
        if hasattr(self, 'CANEngine') and self.CANEngine is not None:
            self.CANEngine.stop_loop()
            self.CANEngine = None
