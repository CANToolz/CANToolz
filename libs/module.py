'''
Generic class for modules
'''  
        
#Generic class for all modules       
class CANModule:
    name="Abstract CANSploit module"
    help="No help available"
    id = 0
    outbuf=""
    version=0.0
    
        
    def dprint(self,level,msg):
        str = self.__class__.__name__+ ": " + msg
        if level<= self.DEBUG:
            print str
        
    def rawWrite(self,string): # Used for direct input
        self.dprint(1,"Not supported")
        
    def doEffect(self, CANMsg=None,args={}): # Effect (could be fuzz operation, sniff, filter or whatever)
        return CANMsg
        
    def getName(self):
        return self.name 
        
    def getHelp(self):
        return self.help
        
    def __init__(self, params={}):
        if 'debug' in params:
            self.DEBUG=int(params['debug'])
        else:
            self.DEBUG=0
        
        if 'bus' in params:
            self._bus=int(params['debug'])
        
        self.doInit(params)
        
    def doInit(self,params={}): # Call for some pre-calculation 
        return 0
        
    def doStop(self,params={}): # Stop activity of this module
        return 0    
    def doStart(self,params={}): # Start activity of this module
        return 0        
    def doRead(self,params={}): 
        return 0
    def doWrite(self,params={}):
        return 0 
        