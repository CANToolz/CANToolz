import time

from ..utils import TestCANToolz


class TestAnalyze(TestCANToolz):

    def test_analyze(self):
        self.CANEngine.load_config('tests/configurations/conf_analyze.py')
        self.CANEngine.edit_module(1, {'pipe': 2})
        time.sleep(1)
        self.CANEngine.start_loop()
        # Send several CAN packets to the bus.
        self.CANEngine.call_module(0, 't 4:4:11223344')
        time.sleep(1)
        self.CANEngine.call_module(0, 't 4:4:11223344')
        time.sleep(1)
        self.CANEngine.call_module(0, 't 4:8:1122334411111111')
        time.sleep(1)
        self.CANEngine.call_module(0, 't 1:4:11223344')
        time.sleep(1)
        self.CANEngine.call_module(0, 't 455678:8:1122334411223344')
        time.sleep(1)
        self.CANEngine.call_module(0, 't 4:4:1122334455')
        time.sleep(1)
        index = 1
        # Print table of sniffed CAN packets from analyze.
        ret = self.CANEngine.call_module(1, 'p')
        print(ret)
        _bodyList = self.CANEngine.actions[index][1]._bodyList

        self.assertTrue(4 in _bodyList, "We should be able to find ID 4")
        self.assertTrue(455678 in _bodyList, "We should be able to find ID 455678")
        self.assertFalse(2 in _bodyList, "We should not be able to find ID 2")
        self.assertFalse(0 in _bodyList, "We should not be able to find ID 0")
        # Clear sniffed CAN packets table from analyze
        self.CANEngine.call_module(1, 'c')
        # Send one CAN packet to the bus.
        self.CANEngine.call_module(0, 't 2:8:1122334411223344')
        time.sleep(1)
        # Print table of sniffed CAN packets from analyze.
        self.CANEngine.call_module(1, 'p')
        _bodyList = self.CANEngine.actions[index][1]._bodyList
        self.assertFalse(4 in _bodyList, "We should not be able to find ID 4")
        self.assertFalse(455678 in _bodyList, "We should not be able to find ID 455678")
        self.assertTrue(2 in _bodyList, "We should be able to find ID 2")

    def test_analyze_diff(self):
        self.CANEngine.load_config('tests/configurations/conf_replay_uds.py')
        self.CANEngine.start_loop()
        time.sleep(1)
        # Replay loaded packets via replay.
        self.CANEngine.call_module(0, 'r 0-3')
        time.sleep(1)
        # Switch sniffing to a new buffer.
        self.CANEngine.call_module(1, 'D')
        time.sleep(1)
        # Replay loaded packets via replay.
        self.CANEngine.call_module(0, 'r 0-3')
        time.sleep(1)
        # Print diff between two buffers.
        ret = self.CANEngine.call_module(1, 'I')
        self.assertFalse(0 <= ret.find(" 0x707 "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x2bc "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x70b "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x709 "), "Should be empty diff")
        # Replay loaded packets via replay.
        self.CANEngine.call_module(0, 'r 0-6')
        time.sleep(1)
        # Print diff between two buffers.
        ret = self.CANEngine.call_module(1, 'I')
        print(ret)
        self.assertTrue(0 <= ret.find(" 0x707 "), "Should be empty diff")
        self.assertTrue(0 <= ret.find(" 0x708 "), "Should be empty diff")
        self.assertTrue(0 <= ret.find("03410d00"), "Should not be empty diff")
        self.assertTrue(0 <= ret.find("1014490201314731"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find(" 0x2bc "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x70b "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x709 "), "Should be empty diff")

        # Replay loaded packets via replay.
        self.CANEngine.call_module(0, 'r 0-6')
        time.sleep(1)
        # Print diff between two buffers and show only new IDs.
        ret = self.CANEngine.call_module(1, 'N')
        print(ret)
        self.assertTrue(0 <= ret.find(" 0x707 "), "Should be empty diff")
        self.assertTrue(0 <= ret.find(" 0x708 "), "Should be empty diff")
        self.assertTrue(0 <= ret.find("03410d00"), "Should not be empty diff")
        self.assertTrue(0 <= ret.find("1014490201314731"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find(" 0x2bc "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x70b "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x709 "), "Should be empty diff")

        # Switch sniffing to a new buffer.
        self.CANEngine.call_module(1, 'D , TEST BUFF')
        # Replay loaded packets via replay.
        self.CANEngine.call_module(0, 'r 0-6')
        time.sleep(1)
        # Switch sniffing to a new buffer.
        self.CANEngine.call_module(1, 'D , TEST BUFF2')
        # Replay loaded packets via replay.
        self.CANEngine.call_module(0, 'r')
        time.sleep(1)
        # Print diff between two buffers.
        ret = self.CANEngine.call_module(1, 'I 2,3')
        self.assertFalse(0 <= ret.find(" 0x707 "), "Should be empty diff")
        self.assertTrue(0 <= ret.find(" 0x708 "), "Should be empty diff")
        self.assertFalse(0 <= ret.find("03410d00"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find("1014490201314731"), "Should be empty diff")
        self.assertTrue(0 <= ret.find("215a543533383236"), "Should not be empty diff")
        self.assertTrue(0 <= ret.find("2246313039313439"), "Should not be empty diff")

        # Print diff between two buffers.
        ret = self.CANEngine.call_module(1, 'I 2,3,2')
        self.assertFalse(0 <= ret.find(" 0x707 "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x708 "), "Should be empty diff")
        self.assertFalse(0 <= ret.find("03410d00"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find("1014490201314731"), "Should be empty diff")
        self.assertFalse(0 <= ret.find("215a543533383236"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find("2246313039313439"), "Should not be empty diff")

        # Print diff between two buffers.
        ret = self.CANEngine.call_module(1, 'I 2,3,3')
        self.assertFalse(0 <= ret.find(" 0x707 "), "Should be empty diff")
        self.assertTrue(0 <= ret.find(" 0x708 "), "Should be empty diff")
        self.assertFalse(0 <= ret.find("03410d00"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find("1014490201314731"), "Should be empty diff")
        self.assertTrue(0 <= ret.find("215a543533383236"), "Should not be empty diff")
        self.assertTrue(0 <= ret.find("2246313039313439"), "Should not be empty diff")

        # Print diff between two buffers and show only new IDs.
        ret = self.CANEngine.call_module(1, 'N')
        self.assertFalse(0 <= ret.find(" 0x707 "), "Should be empty diff")
        self.assertFalse(0 <= ret.find(" 0x708 "), "Should be empty diff")
        self.assertFalse(0 <= ret.find("03410d00"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find("1014490201314731"), "Should be empty diff")
        self.assertFalse(0 <= ret.find("215a543533383236"), "Should not be empty diff")
        self.assertFalse(0 <= ret.find("2246313039313439"), "Should not be empty diff")

    def test_analyze_fields(self):
        self.CANEngine.load_config('tests/configurations/conf_replay_uds.py')
        self.CANEngine.start_loop()
        time.sleep(1)
        # Clean replay loaded table.
        self.CANEngine.call_module(0, 'c')
        time.sleep(1)
        # Load CAN messages from file into replay.
        self.CANEngine.call_module(0, 'l tests/data/test_fields.dump')
        time.sleep(1)
        # Replay loaded CAN message with replay.
        self.CANEngine.call_module(0, 'r')
        time.sleep(1)
        analyze = 1
        # Show detected amount of fields for a chosen ECU.
        ret1 = self.CANEngine.call_module(analyze, 'show')
        # Show fields value for a chosen ECU, in hex.
        ret2 = self.CANEngine.call_module(analyze, 'fields 2, hex')
        print(ret1)
        self.assertTrue(0 <= ret1.find("ECU: 0x2     Length: 2     FIELDS DETECTED: 2"), "Should be found")
        self.assertTrue(0 <= ret1.find("ECU: 0x1     Length: 7     FIELDS DETECTED: 2"), "Should be found")
        self.assertTrue(0 <= ret1.find("ECU: 0x1     Length: 8     FIELDS DETECTED: 3"), "Should be found")
        print(ret2)
        self.assertTrue(0 <= ret2.find("1111    0"), "Should be found")
        self.assertTrue(0 <= ret2.find("1110    0"), "Should be found")

        # Show fields value for a chosen ECU, in binary.
        ret2 = self.CANEngine.call_module(analyze, "fields 2, bin")
        print(ret2)
        self.assertTrue(0 <= ret2.find("1000100010001    000"), "Should be found")
        self.assertTrue(0 <= ret2.find("1000100010000    001"), "Should be found")

        # Show fields value for a chosen ECU, in decimal.
        ret2 = self.CANEngine.call_module(analyze, "fields 1, int")

        self.assertTrue(0 <= ret2.find("1    1    9626517791733640"), "Should be found")
        self.assertTrue(0 <= ret2.find("2    2    9626517791733640"), "Should be found")
        self.assertTrue(0 <= ret2.find("3    3    9626517791733640"), "Should be found")
        self.assertTrue(0 <= ret2.find("17895699    17895697"), "Should be found")
        self.assertTrue(0 <= ret2.find("17895697    17895697"), "Should be found")

    def test_analyze_meta_add(self):
        self.CANEngine.load_config('tests/configurations/conf_replay_uds.py')
        self.CANEngine.start_loop()
        time.sleep(1)
        # Replay loaded CAN message with replay.
        self.CANEngine.call_module(0, 'r 0-9')
        time.sleep(2)
        analyze = 1
        # Add meta description for several CAN frames.
        self.CANEngine.call_module(analyze, 'i 0x708 ,.*, TEST UDS')
        self.CANEngine.call_module(analyze, 'i 0x2bc , 0f410d00 , TEST 700')
        self.CANEngine.call_module(analyze, 'i 1803 , 2f............44 , TEST 1803')
        self.CANEngine.call_module(analyze, 'i 1801 , 036f , TEST 1801')
        # Save meta description to file.
        self.CANEngine.call_module(analyze, 'z tests/data/meta.txt')
        # Print table of sniffed CAN packets from analyze.
        ret = self.CANEngine.call_module(analyze, 'p')
        print(ret)
        idx = ret.find("TEST UDS")
        self.assertTrue(0 <= idx, "Comment 'TEST UDS' should be found 1 times")
        idx2 = ret.find("TEST UDS", idx + 8)
        self.assertTrue(0 <= idx2, "Comment 'TEST UDS' should be found 2 times")
        self.assertTrue(0 <= ret.find("TEST 700"), "Comment 'TEST 700' should be found 1 times")
        self.assertTrue(0 <= ret.find("TEST 1803"), "Comment 'TEST 1803' should be found 1 times")
        self.assertFalse(0 <= ret.find("TEST 1801"), "Comment 'TEST 1801' should NOT be found 1 times")

    def test_analyze_meta_load(self):
        self.CANEngine.load_config('tests/configurations/conf_replay_uds.py')
        self.CANEngine.start_loop()
        time.sleep(1)
        # Replay loaded CAN message with replay.
        self.CANEngine.call_module(0, 'r 0-9')
        time.sleep(2)
        analyze = 1
        # Print table of sniffed CAN packets from analyze.
        ret = self.CANEngine.call_module(analyze, 'p')
        idx = ret.find("TEST UDS")
        self.assertTrue(-1 == idx, "Comment 'TEST UDS' should NOT be found")
        # Load meta description from file.
        self.CANEngine.call_module(analyze, 'l tests/data/meta.txt')
        # Print table of sniffed CAN packets from analyze.
        ret = self.CANEngine.call_module(analyze, 'p')
        print(ret)
        # Save buffer stats in CSV format to file.
        self.CANEngine.call_module(analyze, 'd tests/data/meta_test.csv')
        idx = ret.find("TEST UDS")
        self.assertTrue(0 <= idx, "Comment 'TEST UDS' should be found 1 times")
        idx2 = ret.find("TEST UDS", idx + 8)
        self.assertTrue(0 <= idx2, "Comment 'TEST UDS' should be found 2 times")
        self.assertTrue(0 <= ret.find("TEST 700"), "Comment 'TEST 700' should be found 1 times")
        self.assertTrue(0 <= ret.find("TEST 1803"), "Comment 'TEST 1803' should be found 1 times")
        self.assertFalse(0 <= ret.find("TEST 1801"), "Comment 'TEST 1801' should NOT be found 1 times")
