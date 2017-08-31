import time

from ..utils import TestCANToolz


class TestFirewall(TestCANToolz):

    def test_blocked_body_hex(self):
        self.CANEngine.load_config('tests/configurations/conf_analyze.py')
        self.CANEngine.edit_module(2, {'pipe': 2, 'hex_black_body': ['0102030605']})
        self.CANEngine.start_loop()
        index = 3

        self.CANEngine.call_module(0, 't 4:6:010203060505')  # pass
        time.sleep(1)
        mod = self.CANEngine.actions[index][1].CANList
        self.assertFalse(len(mod) == 0, "We should find message in PIPE")
        self.assertTrue(mod[-1].frame_id == 4, "We should be able to find ID 4")

        self.CANEngine.actions[index][1].CANList = []

        self.CANEngine.call_module(0, 't 4:5:0102030605')  # blocked

        mod = self.CANEngine.actions[index][1].CANList
        self.assertTrue(len(mod) == 0, "We should NOT find message in PIPE")
        self.CANEngine.actions[index][1].CANList = []

        self.CANEngine.edit_module(2, {'pipe': 2, 'hex_white_body': ['0102030605']})

        self.CANEngine.call_module(0, 't 4:5:0102030605')  # pass
        time.sleep(1)
        mod = self.CANEngine.actions[index][1].CANList
        self.assertFalse(len(mod) == 0, "We should find message in PIPE")
        self.assertTrue(mod[-1].frame_id == 4, "We should be able to find ID 4")
        self.CANEngine.actions[index][1].CANList = []

        self.CANEngine.call_module(0, 't 4:6:010203060505')  # blocked

        mod = self.CANEngine.actions[index][1].CANList
        self.assertTrue(len(mod) == 0, "We should NOT find message in PIPE")
        self.CANEngine.actions[index][1].CANList = []

    def test_blocked_body(self):
        self.CANEngine.load_config('tests/configurations/conf_analyze.py')
        self.CANEngine.edit_module(2, {'pipe': 2, 'black_body': [[1, 2, 3, 6, 5]]})
        self.CANEngine.start_loop()
        index = 3

        self.CANEngine.call_module(0, 't 4:6:010203060505')  # pass
        time.sleep(1)
        mod = self.CANEngine.actions[index][1].CANList
        self.assertFalse(len(mod) == 0, "We should find message in PIPE")
        self.assertTrue(mod[-1].frame_id == 4, "We should be able to find ID 4")
        self.CANEngine.actions[index][1].CANList = []

        self.CANEngine.call_module(0, 't 4:5:0102030605')  # blocked

        mod = self.CANEngine.actions[index][1].CANList
        self.assertTrue(len(mod) == 0, "We should NOT find message in PIPE")
        self.CANEngine.actions[index][1].CANList = []

        self.CANEngine.edit_module(2, {'pipe': 2, 'white_body': [[1, 2, 3, 6, 5]]})

        self.CANEngine.call_module(0, 't 4:5:0102030605')  # pass
        time.sleep(1)
        mod = self.CANEngine.actions[index][1].CANList
        self.assertFalse(len(mod) == 0, "We should find message in PIPE")
        self.assertTrue(mod[-1].frame_id == 4, "We should be able to find ID 4")
        self.CANEngine.actions[index][1].CANList = []

        self.CANEngine.call_module(0, 't 4:6:010203060505')  # blocked

        mod = self.CANEngine.actions[index][1].CANList
        self.assertTrue(len(mod) == 0, "We should NOT find message in PIPE")
        self.CANEngine.actions[index][1].CANList = []

    def test_blocked_id(self):
        self.CANEngine.load_config('tests/configurations/conf_analyze.py')
        self.CANEngine.edit_module(2, {'pipe': 2, 'black_list': [1, 2, 3, 6, 5]})
        self.CANEngine.start_loop()
        index = 3

        self.CANEngine.call_module(0, 't 4:4:11223344')  # pass
        time.sleep(1)
        mod = self.CANEngine.actions[index][1].CANList
        self.assertFalse(len(mod) == 0, "We should find message in PIPE")
        self.assertTrue(mod[-1].frame_id == 4, "We should be able to find ID 4")
        self.CANEngine.actions[index][1].CANList = []

        self.CANEngine.call_module(0, 't 1:4:11223344')
        time.sleep(1)
        mod = self.CANEngine.actions[index][1].CANList
        self.assertFalse(len(mod) > 0, "Message number 1 should not pass")
        self.CANEngine.actions[index][1].CANList = []

        self.CANEngine.call_module(0, 't 7:4:11223344')  # pass
        time.sleep(1)
        mod = self.CANEngine.actions[index][1].CANList
        self.assertTrue(mod[-1].frame_id == 7, "We should be able to find ID 7")
        self.CANEngine.actions[index][1].CANList = []

        self.CANEngine.call_module(0, 't 1:4:11223344')
        time.sleep(1)
        mod = self.CANEngine.actions[index][1].CANList
        self.assertFalse(len(mod) > 0, "Message number 1 should not pass")
        self.CANEngine.actions[index][1].CANList = []
        self.CANEngine.call_module(0, 't 1:8:1122334411223344')
        time.sleep(1)
        mod = self.CANEngine.actions[index][1].CANList
        self.assertFalse(len(mod) > 0, "Message number 1 should not pass")
        self.CANEngine.actions[index][1].CANList = []

        self.CANEngine.call_module(0, 't 4:4:11223344')  # pass
        time.sleep(1)
        mod = self.CANEngine.actions[index][1].CANList
        self.assertTrue(mod[-1].frame_id == 4, "We should be able to find ID 4")
        self.CANEngine.actions[index][1].CANList = []
