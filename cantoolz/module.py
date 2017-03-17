"""
Generic class for modules
"""

import threading
import collections
import codecs
import traceback


class Command(object):

    """Command class helper to easily identify command attributes."""

    def __init__(self, description, num_params, desc_params, callback, is_enabled, index=0):
        #: Description of what the command does.
        self.description = description
        #: Number of parameters.
        self.num_params = num_params
        #: Description of the parameters if any.
        self.desc_params = desc_params
        #: Function to call when executing the command.
        self.callback = callback
        #: Command is enabled (or not).
        self.is_enabled = is_enabled
        #: index
        self.index = index


class CANModule:

    """Generic class for all modules.

    Defines all default behaviors that must/should be overriden by other modules.
    """

    #: Name of the module.
    name = 'Abstract CANSploit module'
    #: Help of the module (can be multiline).
    help = 'No help available'
    #: ID of the module.
    id = 0
    #: Version of the module.
    version = 0.0
    #: Debug flag for verbose output.
    DEBUG = 0

    _active = True  # True if module is enabled. False otherwise.
    _timeout = 3  # Maximum timeout value when running thread
    thr_block = threading.Event()  # Blocking mode (using events)

    def __init__(self, params):
        """Initialize the module.

        :param dict param: Parameters of the module.
        """
        self.DEBUG = int(params.get('debug', 0))
        self._bus = params.get('bus', self.__class__.__name__)
        self._active = False if params.get('active') in ["False", "false", "0", "-1"] else True
        # List of default commands supported by the module.
        self._cmdList = collections.OrderedDict()  # Command list (doInit section)
        self._cmdList['S'] = Command('Current status', 0, '', self.get_status, True)
        self._cmdList['s'] = Command('Stop/Activate current module', 0, '', self.do_activate, True)
        self._status = 0
        self._error_text = ""
        self.do_init(params)

    @staticmethod
    def get_hex(bytes_in):
        """Get hexadecimal representation of `bytes_in`."""
        return (codecs.encode(bytes_in, 'hex_codec')).decode("ISO-8859-1")

    @property
    def is_active(self):
        """Module is active or not.

        :returns: boolean -- `True` if module is active, `False` otherwise.
        """
        return self._active

    def get_status(self, def_in=0):
        """Human-representation of the module status.

        :returns: str -- Human-readable status of the module.
        """
        return 'Current status: {0}'.format(self._active)

    def do_activate(self, def_in=0, mode=-1):
        """Force the status of the module to `mode`.

        :param int mode: Mode the module should be switched to (default: `-1`)
          - `0` module is switched off
          - `-1` module is switched to the opposite of its current state (active -> inactive / inactive -> active)
          - else module is switched on

        :returns: str -- Human-readable status of the module.
        """
        if mode == -1:
            self._active = not self._active
        elif mode == 0:
            self._active = False
        else:
            self._active = True
        return 'Active status: {0}'.format(self._active)

    def dprint(self, level, msg):
        """Print function for debugging purpose."""
        str_msg = '{0}: {1}'.format(self.__class__.__name__, msg)
        if level <= self.DEBUG:
            print(str_msg)

    def raw_write(self, string):  # Used for direct input
        """Call the command specified in `string` and return its result.

        :param str string: The full command with its paramaters (e.g. 's' to stop the module)

        :returns: str -- Result of the command execution.
        """
        ret = ''
        self.thr_block.wait(timeout=self._timeout)  # Timeout of 3 seconds
        self.thr_block.clear()
        full_cmd = string.lstrip()
        if ' ' in full_cmd:  # Any parameters specified?
            in_cmd, parameters = full_cmd.split(' ', maxsplit=1)
        else:
            in_cmd = full_cmd
            parameters = None
        if in_cmd in self._cmdList:
            cmd = self._cmdList[in_cmd]
            if cmd.is_enabled:
                try:
                    if parameters:
                        ret = cmd.callback(cmd.index, parameters)
                    else:
                        ret = cmd.callback(cmd.index)
                except Exception as e:
                    #self.set_error_text("ERROR: " + str(e))
                    ret = "ERROR: " + str(e)
                    traceback.print_exc()
            else:
                ret = 'Error: command is disabled!'
        self.thr_block.set()
        return ret

    def do_effect(self, can_msg, args):
        """Function to override when implementing an effect (fuzzing, sniffer, filtering operations, etc.)

        :returns: str -- CAN message after effect has been applied.
        """
        return can_msg

    def get_name(self):
        """Get the name of the module.

        :returns: str -- Name of the module.
        """
        return self.name

    def get_help(self):
        """Get the help of the module.

        :returns: str -- Help of the module.
        """
        return self._cmdList

    def get_status_bar(self):
        """Get the status of the module.

        :returns: dict -- 'bar': Progress abr of the module. 'text': Current text for errors and notifications
        """
        self.thr_block.wait(timeout=self._timeout)
        self.thr_block.clear()
        status = int(self._status)
        error_text = ""
        if self._error_text != "":
            error_text = self._error_text
            self._error_text = ""
        self.thr_block.set()

        return {'bar': status,'text': error_text}

    def set_error_text(self, text):
        """Function to set current notification or error

        :returns: int -- Status of init.
        """
        print("!!! "+text)
        self._error_text = self.__class__.name + ": " + text

    def do_init(self, params):
        """Function to perform calculations before doing any actual work.

        :returns: int -- Status of init.
        """
        return 0

    def do_stop(self, params):
        """Function called when stopping activity of the module.

        :returns: int -- Status of stop.
        """
        return 0

    def do_start(self, params):
        """Function called when starting activity of the module.

        :returns: int -- Status of start.
        """
        return 0

    def do_exit(self, params):
        """Function called when exiting activity of the module.

        :returns: int -- Status of exit.
        """
        return 0
