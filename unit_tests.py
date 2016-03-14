import sys
import unittest
import time

class ModUdsTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_fuzz_can(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_6.py")
        self.CANEngine.edit_module(0, {'range': [111,112], 'data': [0,1], 'delay': 0})
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "s")
        time.sleep(3)
        ret = self.CANEngine.call_module(3, "p")
        # print ret
        index = 3
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue( 511 == len(_bodyList[111]),"511 uiniq packets, should be sent")

    def test_fuzz_iso(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_6.py")
        self.CANEngine.edit_module(0, {'range': [111,112], 'data': [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],\
                                       'delay': 0,'index':[5,16],'mode':'ISO'})
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "s")
        time.sleep(3)
        ret = self.CANEngine.call_module(3, "p")
        # print ret
        index = 3
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(513 == len(_bodyList[111]),"513 uiniq packets, should be sent")

class ModUdsTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_replay1(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_5.py")
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(2, "s")
        time.sleep(2)
        index = 1
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(len(_bodyList) == 4, "Should be 4 groups of packets")
        self.assertTrue(1790 in _bodyList, "1790 should be there")
        self.assertTrue(1791 in _bodyList, "1791 should be there")
        self.assertTrue(1792 in _bodyList, "1792 should be there")
        self.assertTrue((3, "02010d".decode('hex'), 0, False) in _bodyList[1792], "020902 as packet should be there")
        self.assertTrue((7, "062f0307030000".decode('hex'), 0, False) in _bodyList[1792],
                        "062f0307030000 as packet should be there")
        self.assertTrue((3, "020902".decode('hex'), 0, False) in _bodyList[1792], "020901 as packet should be there")
        self.assertTrue((3, "02010d".decode('hex'), 0, False) in _bodyList[1790], "02010d as packet should be there")
        self.assertFalse((3, "020904".decode('hex'), 0, False) in _bodyList[1791],
                         "020904 as packet should not be there")
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        ret = self.CANEngine.call_module(1, "p")
        print(ret)
        self.CANEngine.call_module(0, "r 0-9")
        time.sleep(2)
        ret = self.CANEngine.call_module(1, "p")
        print(ret)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        ret = self.CANEngine.call_module(1, "a")
        print(ret)
        _udsList = self.CANEngine._enabledList[index][1].UDSList.sessions
        self.assertTrue(1 == _bodyList[1800][(
            8,
            "1014490201314731".decode('hex'),
            0,
            False
        )], "Should be 1 packed replayed")
        self.assertTrue(1791 in _udsList, "1791 should be there")
        self.assertTrue(1792 in _udsList, "1792 should be there")
        self.assertTrue(1793 in _udsList, "1793 should be there")
        self.assertTrue(1 in _udsList[1791], "1 should be there")
        self.assertTrue(0x2f in _udsList[1793], "0x2f should be there")
        self.assertTrue(0x09 in _udsList[1792], "0x09 should be there")
        self.assertTrue(2 == _udsList[1792][9]['sub'], "2 should be there")
        self.assertTrue(3 == _udsList[1793][0x2f]['sub'], "3 should be there")
        self.assertTrue(1 == _udsList[1791][1]['status'], "Status should be 1")
        self.assertTrue(1 == _udsList[1792][9]['status'], "Status should be 1")
        self.assertTrue(2 == _udsList[1793][0x2f]['status'], "Status should be 2")

        self.assertTrue(0 == _udsList[1791][0x2f]['status'], "Status should be 0")
        self.assertTrue(0 == _udsList[1791][0x9]['status'], "Status should be 0")
        self.assertTrue(0 == _udsList[1793][0x1]['status'], "Status should be 0")
        self.assertTrue(0 == _udsList[1793][0x9]['status'], "Status should be 0")



class ModReplayTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_replay1(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_3.py")
        self.CANEngine.start_loop()
        time.sleep(2)
        self.CANEngine.call_module(2, "s")
        num = self.CANEngine.call_module(1, "p")
        time.sleep(1)
        self.assertTrue(int(num) == 0, "Should be be 0 packets")
        self.CANEngine.call_module(1, "g")
        self.CANEngine.call_module(0, "t 4:8:1122334411111111")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 4:8:1122334411111111")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 666:8:1122334411111111")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 5:8:1122334411111111")
        time.sleep(1)
        num = self.CANEngine.call_module(1, "p")
        time.sleep(1)
        print("num is " + num)
        self.assertTrue(int(num) == 4, "Should be be 4 packets")
        ret = self.CANEngine.call_module(1, "d 0-4")
        time.sleep(1)
        print(ret)
        self.CANEngine.call_module(2, "s")
        time.sleep(1)
        self.CANEngine.call_module(1, "r 0-4")
        time.sleep(1)
        self.CANEngine.call_module(1, "c")
        time.sleep(1)
        num = self.CANEngine.call_module(1, "p")
        time.sleep(1)
        self.assertTrue(int(num) == 0, "Should be be 0 packets")
        index = 2
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        ret = self.CANEngine.call_module(2, "p")
        print(ret)
        self.assertTrue(len(_bodyList) == 3, "Should be be 3 groups found")

    def test_replay2(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_4.py")
        self.CANEngine.start_loop()
        num = self.CANEngine.call_module(1, "p")
        time.sleep(1)
        print("num is " + num)
        self.assertTrue(int(num) == 4, "Should be be 4 packets")
        index = 2
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(len(_bodyList) == 0, "Should be 0 packets sent")
        self.CANEngine.call_module(1, "r 2-4")
        time.sleep(1)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        ret = self.CANEngine.call_module(2, "p")
        print(ret)
        self.assertTrue(2 == len(_bodyList), "Should be 2 packets sent")
        self.assertTrue(666 in _bodyList, "ID 666 should be dound")
        self.assertTrue(5 in _bodyList, "ID 5 should be found")
        self.assertFalse(4 in _bodyList, "ID 4 should not be found ")
        self.CANEngine.call_module(2, "r tests/new.save")
        self.CANEngine.call_module(2, "c")
        self.CANEngine.call_module(1, "l tests/new.save")
        ret = self.CANEngine.call_module(1, "p")
        print(ret)
        self.assertTrue(int(ret) == 6, "Should be 6 packets")



class ModPingTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()

    def test_isoanal(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_2.py")
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
        self.CANEngine.call_module(0, "s")
        self.CANEngine.call_module(1, "s")
        time.sleep(1)
        ret = self.CANEngine.call_module(3, "p")
        print(ret)
        ret = self.CANEngine.call_module(3, "a")
        print(ret)
        self.assertTrue(ret.find("ID 542999") > 0, "Should be be found 542999")
        self.assertTrue(ret.find("ID 543000") > 0, "Should be found 543000")
        self.assertFalse(ret.find("ID 543002") > 0, "Should not be found 543002")

    def test_emptyConfig(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_2.py")
        self.CANEngine.edit_module(0, {
            'pipe': 2,
            'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233',
            'mode': 'isotp'
        })
        self.CANEngine.start_loop()
        self.CANEngine.call_module(0, "s")
        time.sleep(1)
        index = 3
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(len(_bodyList) == 0, "Should be empty list")

    def test_ping(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_2.py")
        self.CANEngine.edit_module(0, {
            'pipe': 2,
            'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233',
            'range': [542999, 543002],
            'mode': 'isotp'
        })
        self.CANEngine.start_loop()
        time.sleep(1)
        self.CANEngine.call_module(0, "s")
        time.sleep(1)
        index = 3
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
        self.CANEngine.stop_loop()

    def test_stat(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_1.conf")
        self.CANEngine.edit_module(1, {'pipe': 2})
        time.sleep(1)
        self.CANEngine.start_loop()
        self.CANEngine.call_module(0, "t 4:4:11223344")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 4:4:11223344")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 4:8:1122334411111111")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 1:4:11223344")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 455678:8:1122334411223344")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 4:4:1122334455")
        time.sleep(1)
        index = 1
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        ret = self.CANEngine.call_module(1, "p")
        print(ret)
        self.assertTrue(4 in _bodyList, "We should be able to find ID 4")
        self.assertTrue(455678 in _bodyList, "We should be able to find ID 455678")
        self.assertFalse(2 in _bodyList, "We should not be able to find ID 2")
        self.assertFalse(0 in _bodyList, "We should not be able to find ID 0")

        self.CANEngine.call_module(1, "m 0")
        time.sleep(1)
        can_str = self.CANEngine.call_module(1, "p")
        time.sleep(1)
        print(can_str)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList

        self.assertTrue(0 in _bodyList, "We should be able to find ID 0")
        self.assertTrue(2 == _bodyList[4][(4, "11223344".decode('hex'), 31, False)], "We should be found 2 messages")

        self.CANEngine.call_module(1, "c")
        time.sleep(1)
        self.CANEngine.call_module(0, "t 2:8:1122334411223344")
        time.sleep(1)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList

        self.assertFalse(4 in _bodyList, "We should not be able to find ID 4")
        self.assertFalse(455678 in _bodyList, "We should not be able to find ID 455678")
        self.assertTrue(2 in _bodyList, "We should be able to find ID 2")


class ModFirewallTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stop_loop()

    def test_blockedBody(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_1.py")
        self.CANEngine.edit_module(2, {'pipe': 2, 'black_body': [1, 2, 3, 6, 5]})
        self.CANEngine.start_loop()
        index = 3

        self.CANEngine.call_module(0, "t 4:6:010203060505")  # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod is None, "We should find message in PIPE")
        self.assertTrue(mod.frame_id == 4, "We should be able to find ID 4")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.call_module(0, "t 4:5:0102030605")  # blocked
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertTrue(mod is None, "We should NOT find message in PIPE")
        #self.assertFalse(mod.frame_id == 4, "We should be able to find ID 4")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.edit_module(2, {'pipe': 2, 'white_body': [1, 2, 3, 6, 5]})

        self.CANEngine.call_module(0, "t 4:5:0102030605")  # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod is None, "We should find message in PIPE")
        self.assertTrue(mod.frame_id == 4, "We should be able to find ID 4")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.call_module(0, "t 4:6:010203060505")  # blocked
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertTrue(mod is None, "We should NOT find message in PIPE")
        #self.assertFalse(mod.frame_id == 4, "We should be able to find ID 4")
        self.CANEngine._enabledList[index][1].CANList = None

    def test_blockedID(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/test_1.py")
        self.CANEngine.edit_module(2, {'pipe': 2, 'black_list': [1, 2, 3, 6, 5]})
        self.CANEngine.start_loop()
        index = 3

        self.CANEngine.call_module(0, "t 4:4:11223344")  # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod is None, "We should find message in PIPE")
        self.assertTrue(mod.frame_id == 4, "We should be able to find ID 4")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.call_module(0, "t 1:4:11223344")
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod, "Message number 1 should not pass")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.call_module(0, "t 7:4:11223344")  # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertTrue(mod.frame_id == 7, "We should be able to find ID 7")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.call_module(0, "t 1:4:11223344")
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod, "Message number 1 should not pass")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.call_module(0, "t 1:8:1122334411223344")
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse(mod, "Message number 1 should not pass")
        self.CANEngine._enabledList[index][1].CANList = None

        self.CANEngine.call_module(0, "t 4:4:11223344")  # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertTrue(mod.frame_id == 4, "We should be able to find ID 4")
        self.CANEngine._enabledList[index][1].CANList = None

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
