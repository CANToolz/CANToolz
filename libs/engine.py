from libs.can import *
import sys
import threading
import ConfigParser
import ast

'''
Main class
'''


class CANSploit:
    DEBUG = 0

    def dprint(self, level, msg):
        if level <= self.DEBUG:
            print(self.__class__.__name__ + ": " + msg)

    def __init__(self):
        self._version = "0.9b"  # version
        self._enabledList = []  # queue of active modules with params
        self._pipes = [None, None]  # two pipes with CANMessages
        self._type = {}  # Pointers on instances here
        self._modules = []  # loaded modules
        self._thread = None
        self._mainThread = None
        self._stop = threading.Event()
        self._raw = threading.Event()
        self._idc = -1
        sys.path.append('./modules')
        sys.dont_write_bytecode = True

    # Main loop with two pipes
    def main_loop(self):
        # Run until STOP
        while not self._stop.is_set():
            self._pipes[0] = CANSploitMessage()  # Prepare empty message
            self._pipes[1] = CANSploitMessage()  # Prepare empty message
            for name, module, params, pipe in self._enabledList:  # Each module
                #  Handle CAN message
                if module._active:
                    module.thr_block.wait(3)
                    module.thr_block.clear()
                    self._pipes[pipe] = module.do_effect(self._pipes[pipe], params)  # doEffect on CANMessage
                    module.thr_block.set()

                    # Here when STOP
        for name, module, params, pipe in self._enabledList:
            module.do_stop()

    # Call module command        
    def call_module(self, mod, params):
        x = self.find_module(mod)
        if x >= 0:
            ret = self._enabledList[x][1].raw_write(params)
        else:
            ret = "Module " + mod + " not loaded!"
        return ret

    # Enable loop        
    def start_loop(self):
        self._stop.clear()

        for name, module, params, pipe in self._enabledList:
            module.do_start(params)
            module.thr_block.set()

        self._thread = threading.Thread(target=self.main_loop)

        self._thread.daemon = True
        self._thread.start()

    # Pause loop      
    def stop_loop(self):
        self._stop.set()

    # Having defulat values for id and pipe params    
    def check_params(self, params):
        if 'pipe' in params:
            pipe = 1 if int(params['pipe']) > 2 else int(params['pipe']) - 1
        else:
            params['pipe'] = 1
            pipe = 0

        # if 'enabled' not in params:
        #    params['enabled']=True

        return [params, pipe]

    # Add module and params to the end    
    def push_module(self, mod, params):
        chkd_params = self.check_params(params)
        self._enabledList.append([mod, self._type[mod.split("!")[0]], chkd_params[0], chkd_params[1]])

    # Find index of module with name mod    
    def find_module(self, mod):
        i = 0
        x = -1
        for name, module, params, pipe in self._enabledList:
            if name == mod:
                x = i
                break
            i += 1
        return x

        # Add new params to module named mod

    def edit_module(self, mod, params):
        x = self.find_module(mod)
        if x >= 0:
            chkd_params = self.check_params(params)
            self._enabledList[x][2] = chkd_params[0]
            self._enabledList[x][3] = chkd_params[1]
            return x
        return -1

    # Edit value of parameters of module mod    
    def edit_module_param(self, mod, key, value):
        x = self.find_module(mod)
        if x >= 0:
            self._enabledList[x][2][key] = value
            return x
        return -1

    # Get value of parameter    
    def get_module_param(self, mod, key):
        x = self.find_module(mod)
        if x >= 0:
            return self._enabledList[x][2][key]
        return None

    # Get all modules and parameters    
    def get_modules_list(self):
        return self._enabledList

    # Get all parameters for module named mod    
    def get_module_params(self, mod):
        x = self.find_module(mod)
        if x >= 0:
            return self._enabledList[x][2]
        return None

        # Load and init new module form lib

    def init_module(self, mod, params):
        self._modules.append(__import__(mod.split("~")[0]))
        exec ('cls=self._modules[-1].' + mod.split("~")[0] + '(params)')  # init module
        self._type[mod] = cls

        # Load all modules and params form config file

    def load_config(self, path):  # Load config from file
        config = ConfigParser.ConfigParser()
        config.optionxform = str

        # if 1==1:
        try:
            config.read([path])
            sects = config.sections()

            for mod_name in sects:

                if mod_name == "MITM":  # Load effects order
                    paramz_ = config.items('MITM')

                    for (mod, settings) in paramz_:
                        paramz = ast.literal_eval(settings)
                        self.push_module(mod, paramz)
                        # self._enabledList[mod]=[self._type[_mod],paramz]
                else:  # Load modules
                    paramz_ = config.items(mod_name)
                    paramz = dict((y, x) for y, x in paramz_)
                    self.init_module(mod_name, paramz)

        except Exception as e:
            self._enabledList = []
            self._modules = []
            self.dprint(0, "Can't parse config: " + str(e))
            return -1

        return 1
