import sys
import os
import unittest
import time

class ModUniqPrintTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stopLoop()
        
    def test_blockedID(self):

        self.CANEngine = CANSploit()
        self.CANEngine.loadConfig("tests/test_1.conf")
        self.CANEngine.startLoop()
        self.CANEngine.editModule("mod_uniqPrint",{'pipe':2})
        time.sleep(1)
        self.CANEngine.callModule("hw_fakeIO","t 4:4:11223344")
        time.sleep(1)
        self.CANEngine.callModule("hw_fakeIO","t 4:4:11223344")
        time.sleep(1)
        self.CANEngine.callModule("hw_fakeIO","t 1:4:11223344")
        time.sleep(1)
        self.CANEngine.callModule("hw_fakeIO","t 455678:8:1122334411223344")
        time.sleep(1)
        self.CANEngine.callModule("hw_fakeIO","t 4:4:1122334455")
        time.sleep(1)
        index = self.CANEngine.findModule('mod_uniqPrint')
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        
        self.assertTrue( 4 in _bodyList, "We should be able to find ID 4")
        self.assertTrue( 455678 in _bodyList, "We should be able to find ID 455678")
        self.assertFalse( 2 in _bodyList, "We should not be able to find ID 2")
        self.assertFalse( 0 in _bodyList, "We should not be able to find ID 0")
        
        self.CANEngine.callModule("mod_uniqPrint","m 0")
        time.sleep(1)
        str=self.CANEngine.callModule("mod_uniqPrint","p")
        time.sleep(1)
        print str
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
       
        self.assertTrue( 0 in _bodyList, "We should be able to find ID 0")
        self.assertTrue( 2 == _bodyList[4][((4,"11223344".decode('hex'),31,False))], "We should be found 2 messages")
        
        self.CANEngine.callModule("mod_uniqPrint","c")
        time.sleep(1)
        self.CANEngine.callModule("hw_fakeIO","t 2:8:1122334411223344")
        time.sleep(1)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        
        self.assertFalse( 4 in _bodyList, "We should not be able to find ID 4")
        self.assertFalse( 455678 in _bodyList, "We should not be able to find ID 455678")
        self.assertTrue( 2 in _bodyList, "We should be able to find ID 2")
        
class ModFirewallTests(unittest.TestCase):
    def tearDown(self):
        self.CANEngine.stopLoop()
        
    def test_blockedID(self):

        self.CANEngine = CANSploit()
        self.CANEngine.loadConfig("tests/test_1.conf")
        self.CANEngine.startLoop()
        self.CANEngine.editModule("mod_firewall",{'pipe':2,'black_list':[1,2,3,6,5]})
        
        index = self.CANEngine.findModule('hw_fakeIO~1')
        

        self.CANEngine.callModule("hw_fakeIO","t 4:4:11223344") # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse( mod==None, "We should find message in PIPE")
        self.assertTrue( mod._id==4, "We should be able to find ID 4")
        
        self.CANEngine.callModule("hw_fakeIO","t 1:4:11223344")
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse( mod._id == 1, "Message number 1 should not pass")
        
        self.CANEngine.callModule("hw_fakeIO","t 7:4:11223344") # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertTrue( mod._id==7, "We should be able to find ID 7")
        
        self.CANEngine.callModule("hw_fakeIO","t 1:4:11223344")
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse( mod._id == 1, "Message number 1 should not pass")
        
        self.CANEngine.callModule("hw_fakeIO","t 1:8:1122334411223344")
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertFalse( mod._id == 1, "Message number 1 should not pass")
        
        self.CANEngine.callModule("hw_fakeIO","t 4:4:11223344") # pass
        time.sleep(1)
        mod = self.CANEngine._enabledList[index][1].CANList
        self.assertTrue( mod._id==4, "We should be able to find ID 4")
        

if __name__ == '__main__':

    sys.path.append('./modules')
    from libs.engine import *
    from libs.can import *
    from libs.module import *
    #absPath=os.path.dirname(platform_audit)+"/unit_tests/"
    unittest.main()

else:

    from libs.engine import *
    from libs.can import *
    from libs.module import *