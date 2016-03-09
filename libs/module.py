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
    thr_block = threading.Event()  # Blocking mode (using events)

    @property
    def is_active(self):
        return self._active

    def do_activate(self, mode = -1):
        if mode == -1:
            self._active = not self._active
        elif mode == 0:
            self._active = False
        else:
            self._active = True
        return "Active status: " + str(self._active)

    def dprint(self, level, msg):
        str_msg = self.__class__.__name__ + ": " + msg
        if level <= self.DEBUG:
            print(str_msg)

    def raw_write(self, string):  # Used for direct input
        ret = ""
        self.thr_block.wait(3)
        self.thr_block.clear()
        if string[0] in self._cmdList:
            cmd = self._cmdList[string[0]]
            if len(string) > 2:
                ret = cmd[3](string[2:])
            else:
                ret = cmd[3]()
        self.thr_block.set()
        return ret

    def do_effect(self, can_msg, args):  # Effect (could be fuzz operation, sniff, filter or whatever)
        return can_msg

    def get_name(self):
        return self.name

    def get_help(self):
        ret_text = "\nModule " + self.__class__.__name__ + ": " + self.name + "\n" + self.help + \
                  "\n\nConsole commands:\n"
        for cmd, dat in self._cmdList.iteritems():
            ret_text += "\t" + cmd + " " + dat[2] + "\t\t - " + dat[0] + "\n"
        return ret_text

    def __init__(self, params):

        self.DEBUG = int(params.get('debug', 0))
        self._bus = int(params.get('bus', 0))
        self._active = False if params.get('active') in ["False", "false", "0", "-1"] else True

        self._cmdList = {
            'h': ["List of supported commands", 0, "", self.get_help],
            's': ["Stop/Activate current module", 0, "", self.do_activate]
        }

        self.do_init(params)

    def do_init(self, params):  # Call for some pre-calculation
        return 0

    def do_stop(self, params):  # Stop activity of this module
        return 0

    def do_start(self, params):  # Start activity of this module
        return 0

    def do_read(self, params):
        return 0

    def do_write(self, params):
        return 0
