import time
import codecs

from ..utils import TestCANToolz


class TestPing(TestCANToolz):

    def test_iso_anal(self):
        self.CANEngine.load_config("tests/configurations/conf_ping.py")
        self.CANEngine.edit_module(0, {
            'pipe': 2,
            'range': [542999, 543002],
            'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233',
            'mode': 'isotp'
        })
        self.CANEngine.edit_module(1, {
            'pipe': 1,
            'range': [543002, 543005],
            'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233'
        })
        self.CANEngine.start_loop()
        time.sleep(2)
        # Activate ping modules.
        self.CANEngine.call_module(0, 's')
        self.CANEngine.call_module(1, 's')
        time.sleep(1)
        # Print table of sniffed CAN packets from analyze.
        ret = self.CANEngine.call_module(3, 'p')
        print(ret)
        # Analysis sniffed CAN packets using analyze.
        ret = self.CANEngine.call_module(3, 'a')
        print(ret)
        self.assertTrue(ret.find("ID: 0x84917") > 0, "Should be be found 542999")
        self.assertTrue(ret.find("ID: 0x84918") > 0, "Should be found 543000")
        self.assertFalse(ret.find("ID: 0x8491a") > 0, "Should not be found 543002")

    def test_empty_config(self):
        self.CANEngine.load_config("tests/configurations/conf_ping.py")
        self.CANEngine.edit_module(0, {
            'pipe': 2,
            'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233',
            'mode': 'isotp'
        })
        self.CANEngine.start_loop()
        # Activate ping first module.
        self.CANEngine.call_module(0, 's')
        time.sleep(1)
        index = 3
        _bodyList = self.CANEngine.actions[index][1]._bodyList
        self.assertTrue(len(_bodyList) == 0, "Should be empty list")

    def test_ping(self):
        self.CANEngine.load_config("tests/configurations/conf_ping.py")
        self.CANEngine.edit_module(0, {
            'pipe': 2,
            'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233',
            'range': [542999, 543002],
            'mode': 'isotp'
        })
        self.CANEngine.start_loop()
        time.sleep(1)
        # Activate ping first module.
        self.CANEngine.call_module(0, 's')
        time.sleep(1)
        index = 3
        # Print table of sniffed CAN packets from analyze.
        ret = self.CANEngine.call_module(3, 'p')
        print(ret)

        _bodyList = self.CANEngine.actions[index][1]._bodyList
        self.assertTrue(543000 in _bodyList, "We should be able to find ID 543000")
        self.assertFalse(543002 in _bodyList, "We should not be able to find ID 543002")
        self.assertTrue([1, 1, 1, 1, 1, 1] == list(_bodyList[543001].values()), "We should not be able to find ID")
        self.assertTrue(
            "25112233" == (codecs.encode((list(_bodyList[543001].keys())[5][1]), 'hex_codec')).decode("ISO-8859-1"),
            "Last packet of sec should be like that"
        )
        self.assertTrue(
            "24a1a2a3a4a5a6a7" == (codecs.encode((list(_bodyList[543001].keys())[4][1]), 'hex_codec')).decode("ISO-8859-1"),
            "Last packet of sec should be like that"
        )

    def test_ping_uds(self):
        self.CANEngine.load_config('tests/configurations/conf_replay_uds.py')
        self.CANEngine.edit_module(
            2,
            {
                'pipe': 2,
                'services': [
                    {"service": 1, "sub": [1, 2]},
                    {"service": [2, 3], "sub": 3},
                    {"service": "0x4-0x6", "sub": "0x4-0x6"}],
                'mode': 'UDS',
                'range': [1, 2]
            })
        time.sleep(1)
        self.CANEngine.start_loop()
        time.sleep(1)
        # Start ping module.
        self.CANEngine.call_module(2, 's')
        time.sleep(1)
        analyze = 3
        # Print count of loaded packets.
        ret1 = self.CANEngine.call_module(analyze, 'p 0')
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
        self.CANEngine.load_config('tests/configurations/conf_replay_uds.py')
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
        # Start ping module.
        self.CANEngine.call_module(2, 's')
        time.sleep(1)
        analyze = 3
        # Print count of loaded packets.
        ret1 = self.CANEngine.call_module(analyze, 'p 0')
        print(ret1)
        self.assertTrue(0 <= ret1.find('0x1'), "Should be found")
        self.assertTrue(0 <= ret1.find('0101'), "Should be found")
