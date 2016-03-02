import sys
import unittest
import time


class ModPingTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stopLoop()

    def test_isoanal(self):
        self.CANEngine = CANSploit()
        self.CANEngine.loadConfig("tests/test_2.conf")
        self.CANEngine.startLoop()
        self.CANEngine.editModule("gen_ping", {
            'pipe': 2,
            'range': [542999, 543002],
            'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233',
            'mode': 'isotp'
        })
        self.CANEngine.editModule("gen_ping~1", {
            'pipe': 1,
            'range': [543002, 543005],
            'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233'
        })
        self.CANEngine.callModule("gen_ping", "s")
        self.CANEngine.callModule("gen_ping~1", "s")
        time.sleep(1)
        ret = self.CANEngine.callModule("mod_stat", "a")
        print ret
        self.assertTrue(ret.find("ID 542999") > 0, "Should be be found 542999")
        self.assertTrue(ret.find("ID 543000") > 0, "Should be found 543000")
        self.assertFalse(ret.find("ID 543002") > 0, "Should not be found 543002")

    def test_emptyConfig(self):
        self.CANEngine = CANSploit()
        self.CANEngine.loadConfig("tests/test_2.conf")
        self.CANEngine.startLoop()
        self.CANEngine.editModule("gen_ping", {
            'pipe': 2,
            'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233',
            'mode': 'isotp'
        })
        self.CANEngine.callModule("gen_ping", "s")
        time.sleep(1)
        time.sleep(1)
        index = self.CANEngine.findModule('mod_stat')
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(len(_bodyList) == 0, "Should be empty list")

    def test_ping(self):
        self.CANEngine = CANSploit()
        self.CANEngine.loadConfig("tests/test_2.conf")
        self.CANEngine.startLoop()
        self.CANEngine.editModule("gen_ping", {
            'pipe': 2,
            'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233',
            'range': [542999, 543002],
            'mode': 'isotp'
        })
        self.CANEngine.callModule("gen_ping", "s")
        time.sleep(1)
        index = self.CANEngine.findModule('mod_stat')
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList

        self.assertTrue(543000 in _bodyList, "We should be able to find ID 543000")
        self.assertFalse(543002 in _bodyList, "We should not be able to find ID 543002")
        self.assertTrue([1, 1, 1, 1, 1, 1] == _bodyList[543001].values(), "We should not be able to find ID")
        self.assertTrue(
            "25112233" == _bodyList[543001].keys()[5][1].encode('hex'),
            "Last packet of sec should be like that"
        )
        self.assertTrue(
            "24a1a2a3a4a5a6a7" == _bodyList[543001].keys()[4][1].encode('hex'),
            "Last packet of sec should be like that"
        )


class ModStatTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stopLoop()

    def test_blockedID(self):
        self.CANEngine = CANSploit()
        self.CANEngine.loadConfig("tests/test_1.conf")
        self.CANEngine.startLoop()
        self.CANEngine.editModule("mod_stat", {'pipe': 2})
        time.sleep(1)
        self.CANEngine.callModule("hw_fakeIO", "t 4:4:11223344")
        time.sleep(1)
        self.CANEngine.callModule("hw_fakeIO", "t 4:4:11223344")
        time.sleep(1)
        self.CANEngine.callModule("hw_fakeIO", "t 1:4:11223344")
        time.sleep(1)
        self.CANEngine.callModule("hw_fakeIO", "t 455678:8:1122334411223344")
        time.sleep(1)
        self.CANEngine.callModule("hw_fakeIO", "t 4:4:1122334455")
        time.sleep(1)
        index = self.CANEngine.findModule('mod_stat')
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList

        self.assertTrue(4 in _bodyList, "We should be able to find ID 4")
        self.assertTrue(455678 in _bodyList, "We should be able to find ID 455678")
        self.assertFalse(2 in _bodyList, "We should not be able to find ID 2")
        self.assertFalse(0 in _bodyList, "We should not be able to find ID 0")

        self.CANEngine.callModule("mod_stat", "m 0")
        time.sleep(1)
        canstr = self.CANEngine.callModule("mod_stat", "p")
        time.sleep(1)
        print canstr
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList

        self.assertTrue(0 in _bodyList, "We should be able to find ID 0")
        self.assertTrue(2 == _bodyList[4][(4, "11223344".decode('hex'), 31, False)], "We should be found 2 messages")

        self.CANEngine.callModule("mod_stat", "c")
        time.sleep(1)
        self.CANEngine.callModule("hw_fakeIO", "t 2:8:1122334411223344")
        time.sleep(1)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList

        self.assertFalse(4 in _bodyList, "We should not be able to find ID 4")
        self.assertFalse(455678 in _bodyList, "We should not be able to find ID 455678")
        self.assertTrue(2 in _bodyList, "We should be able to find ID 2")


class ModFirewallTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stopLoop()

    def test_blockedID(self):
        self.CANEngine = CANSploit()
        self.CANEngine.loadConfig("tests/test_1.conf")
        self.CANEngine.startLoop()
        self.CANEngine.editModule("mod_firewall", {'pipe': 2, 'black_list': [1, 2, 3, 6, 5]})

        index = self.CANEngine.findModule('hw_fakeIO~1')

        self.CANEngine.callModule("hw_fakeIO", "t 4:4:11223344")  # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod == None, "We should find message in PIPE")
        self.assertTrue(mod._id == 4, "We should be able to find ID 4")

        self.CANEngine.callModule("hw_fakeIO", "t 1:4:11223344")
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod._id == 1, "Message number 1 should not pass")

        self.CANEngine.callModule("hw_fakeIO", "t 7:4:11223344")  # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertTrue(mod._id == 7, "We should be able to find ID 7")

        self.CANEngine.callModule("hw_fakeIO", "t 1:4:11223344")
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod._id == 1, "Message number 1 should not pass")

        self.CANEngine.callModule("hw_fakeIO", "t 1:8:1122334411223344")
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod._id == 1, "Message number 1 should not pass")

        self.CANEngine.callModule("hw_fakeIO", "t 4:4:11223344")  # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertTrue(mod._id == 4, "We should be able to find ID 4")


if __name__ == '__main__':
    sys.path.append('./modules')
    from libs.engine import *
    from libs.can import *
    from libs.module import *

    # absPath=os.path.dirname(platform_audit) + "/unit_tests/"
    unittest.main()
else:
    from libs.engine import *
    from libs.can import *
    from libs.module import *
