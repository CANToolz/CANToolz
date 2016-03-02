import threading

'''
Generic class for modules
'''


# Generic class for all modules
class CANModule:
    name = "Abstract CANSploit module"
    help = "No help available"
    id = 0
    version = 0.0
    _cmdList = {}  # Command list (doInit section)
    _active = True  # Enabled/Disabled
    _block = threading.Event()  # Blocking mode (using events)

    def doActivate(self):
        if self._active:
            self._active = False
        else:
            self._active = True
        return "Active status: " + str(self._active)

    def dprint(self, level, msg):
        strMsg = self.__class__.__name__ + ": " + msg
        if level <= self.DEBUG:
            print strMsg

    def rawWrite(self, string):  # Used for direct input
        ret = ""
        self._block.wait(3)
        self._block.clear()
        if string[0] in self._cmdList:
            cmd = self._cmdList[string[0]]
            if len(string) > 2:
                ret = cmd[3](string[2:])
            else:
                ret = cmd[3]()
        self._block.set()
        return ret

    def doEffect(self, CANMsg=None, args={}):  # Effect (could be fuzz operation, sniff, filter or whatever)
        return CANMsg

    def getName(self):
        return self.name

    def getHelp(self):
        retText = "\nModule " + self.__class__.__name__ + ": " + self.name + "\n" + self.help + \
                  "\n\nConsole commands:\n"
        for cmd, dat in self._cmdList.iteritems():
            retText += "\t" + cmd + " " + dat[2] + "\t\t - " + dat[0] + "\n"
        return retText

    def __init__(self, params={}):
        if 'debug' in params:
            self.DEBUG = int(params['debug'])
        else:
            self.DEBUG = 0

        if 'bus' in params:
            self._bus = int(params['bus'])

        if 'active' in params:
            if params['active'] == "False" or params['active'] == "false" or \
                params['active'] == "0" or params['active'] == "-1":  # TODO Refactoring
                self._active = False
            else:
                self._active = True

        self._cmdList = {'h': ["List of supported commands", 0, "", self.getHelp],
                         's': ["Stop/Activate current module", 0, "", self.doActivate]}

        self.doInit(params)

    def doInit(self, params={}):  # Call for some pre-calculation
        return 0

    def doStop(self, params={}):  # Stop activity of this module
        return 0

    def doStart(self, params={}):  # Start activity of this module
        return 0

    def doRead(self, params={}):
        return 0

    def doWrite(self, params={}):
        return 0
