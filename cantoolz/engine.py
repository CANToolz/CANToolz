import os
import sys
import imp
import time
import logging
import threading

# from cantoolz.can import *
from cantoolz.can import CANSploitMessage


class CANSploit:

    """
    Main class
    """

    DEBUG = 0
    ascii_logo_c = """

   _____          _   _ _______          _
  / ____|   /\   | \ | |__   __|        | |
 | |       /  \  |  \| |  | | ___   ___ | |____
 | |      / /\ \ | . ` |  | |/ _ \ / _ \| |_  /
 | |____ / ____ \| |\  |  | | (_) | (_) | |/ /
  \_____/_/    \_\_| \_|  |_|\___/ \___/|_/___|


"""

    def dprint(self, level, msg):
        if level <= self.DEBUG:
            print((self.__class__.__name__ + ": " + msg))

    def __init__(self):
        self._version = "3b"  # version
        self._enabledList = []  # queue of active modules with params
        self._pipes = {}  # two pipes with CANMessages
        self._type = {}  # Pointers on instances here
        self._modules = []  # loaded modules
        self._thread = None
        self._mainThread = None
        self._stop = threading.Event()
        self._stop.set()
        self.do_stop_e = threading.Event()
        self.do_stop_e.clear()
        self._raw = threading.Event()
        self._idc = -1
        sys.dont_write_bytecode = True

    # Main loop with two pipes
    def main_loop(self):
        # Run until STOP
        while not self.do_stop_e.is_set():
            self._pipes = {}
            for name, module, params in self._enabledList:  # Each module
                #  Handle CAN message

                if module.is_active:
                    module.thr_block.wait(3)
                    module.thr_block.clear()
                    if params['pipe'] not in self._pipes:
                        self._pipes[params['pipe']] = CANSploitMessage()
                    self.dprint(2, "DO EFFECT" + name)
                    self._pipes[params['pipe']] = module.do_effect(self._pipes[params['pipe']], params)

                    """
                    if error and error_on_bus.get(i, False):
                        self._pipes[params['pipe']] = module.do_effect(self._pipes[params['pipe']], params) # If error, try to fix
                    elif not error:
                        self._pipes[params['pipe']] = module.do_effect(self._pipes[params['pipe']], params) # doEffect on CANMessage

                    if self._pipes[params['pipe']].debugData and self._pipes[params['pipe']].debugText.get('do_not_send', False):
                        error_on_bus[i] = True
                        error = True
                        module.dprint(0,"BUS ERROR detected")
                        self._pipes[params['pipe']].debugData = False
                    elif self._pipes[params['pipe']].debugData and self._pipes[params['pipe']].debugText.get('please_send', False):
                        error_on_bus[i] = False
                        error = False
                        self._pipes[params['pipe']].debugData = False
                        module.dprint(0,"BUS ERROR fixed")
                    i += 1
                    """
                    module.thr_block.set()

        self.dprint(2, "STOPPING...")
        # Here when STOP
        for name, module, params in self._enabledList:
            self.dprint(2, "stopping " + name)
            module.do_stop(params)

        self.do_stop_e.clear()
        self.dprint(2, "STOPPED")

    # Call module command
    def call_module(self, index, params):
        # x = self.find_module(mod)
        x = index
        if x >= 0:
            ret = self._enabledList[x][1].raw_write(params)
        else:
            ret = "Module " + str(index) + " not loaded!"
        return ret

    def engine_exit(self):
        for name, module, params in self._enabledList:
            self.dprint(2, "exit for " + name)
            module.do_exit(params)

    # Enable loop
    def start_loop(self):
        self.dprint(2, "START SIGNAL")
        if self._stop.is_set() and not self.do_stop_e.is_set():
            self.do_stop_e.set()
            for name, module, params in self._enabledList:
                self.dprint(2, "startingg " + name)
                module.do_start(params)
                module.thr_block.set()

            self._thread = threading.Thread(target=self.main_loop)
            self._thread.daemon = True

            self._stop.clear()
            self.do_stop_e.clear()
            self.dprint(2, "GO")
            self._thread.start()
            self.dprint(2, "STARTED")

        return not self._stop.is_set()

    # Pause loop
    def stop_loop(self):
        self.dprint(2, "STOP SIGNAL")
        if not self._stop.is_set() and not self.do_stop_e.is_set():
            self.do_stop_e.set()
            while self.do_stop_e.is_set():
                time.sleep(0.01)

        self._stop.set()
        return 1

    # Current status
    @property
    def status_loop(self):
        return not self._stop.is_set()

    # Having defulat values for id and pipe params
    def check_params(self, params):
        if 'pipe' not in list(params.keys()):
            params['pipe'] = 1
        return params

    # Add module and params to the end    
    def push_module(self, mod, params):
        chkd_params = self.check_params(params)
        self._enabledList.append([mod, self._type[mod.split("!")[0]], chkd_params])

    # Find index of module with name mod    
    def find_module(self, mod):
        i = 0
        x = -1
        for name, module, params in self._enabledList:
            if name == mod:
                x = i
                break
            i += 1
        return x

        # Add new params to module named mod

    def edit_module(self, index, params):
        # x = self.find_module(mod)
        x = index
        if x >= 0:
            chkd_params = self.check_params(params)
            self._enabledList[x][2] = chkd_params
            return x
        return -1

    # Get all modules and parameters    
    def get_modules_list(self):
        return self._enabledList

    # Get all parameters for module named mod    
    def get_module_params(self, index):
        # x = self.find_module(mod)
        x = index
        if x >= 0:
            return self._enabledList[x][2]
        return None

        # Load and init new module form lib

    def init_module(self, mod, params):
        """Dynamically initialize a module.

        Dynamically find and load the module from `modules/`. If the module is not found under `modules/z, then it
        recursively looks inside the subdirectories under `modules/`.

        .. note::

            The module must contain a class with the same name as the module itself. For instance, module `my_Module`
            must contain a class named `my_Module`

        :param str mod: Name of the module to dynamically load.
        :param list params: Parameters to pass to the module class when instanciating the module class.

        """
        mod_name = mod.split('~')[0]
        try:
            loaded_module = imp.load_module(mod_name, *imp.find_module(mod_name, path=['cantoolz/modules']))
        except ImportError:
            for subdir in os.listdir('cantoolz/modules'):
                if os.path.isdir(os.path.join(os.path.abspath('cantoolz/modules'), subdir)):
                    try:
                        loaded_module = imp.load_module(mod_name, *imp.find_module(mod_name, path=['cantoolz/modules/{}'.format(subdir)]))
                        logging.info('Loaded {} from subdirectory {}'.format(mod_name, subdir))
                        break
                    except ImportError:
                        continue
            else:  # No module found anywhere under modules/*
                logging.error('Could not find {}, even in subdirectories...'.format(mod_name))
        # Dynamically instanciate the module class.
        self._type[mod] = getattr(loaded_module, mod_name)(params)

    def load_config(self, fullpath):  # Load config from file
        fullpath = fullpath.replace('\\', '/')
        parts = fullpath.split("/")

        if len(parts) > 1:
            path = '/'.join(parts[0:-1])
            sys.path.append(path)

        mod = parts[-1].split(".")[0]

        config = __import__(mod)
        for module, init_params in config.load_modules.items():
            self.init_module(module, init_params)

        for action in config.actions:
            self.push_module(list(action.keys())[0], list(action.values())[0])
        return 1
