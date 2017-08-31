import os
import sys
import imp
import time
import logging
import threading

from cantoolz.can import CANSploitMessage


class CANSploit:

    """
    Main class implementing the core logic of CANToolz.

    The class is responsible for parsing the user configuration, dynamically load the requested modules and initialize
    them with the requested configuration, setup the pipes and handle the threads.
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
        """Debug print method with debug level to filter output.

        :param int level: Level of debug logging (e.g 0 for lowest verbosity; 10 for highest verbosity)
        :param str msg: Debug message.
        """
        if level <= self.DEBUG:
            print('{}: {}'.format(self.__class__.__name__, msg))

    def __init__(self):
        # List of actions with their parameters to perform during the scenario.
        self._actions = []
        # Dictionary of initialized modules for the scenario
        self._modules = {}
        # Thread reference
        self._thread = None
        self._stop = threading.Event()
        self._stop.set()
        self.do_stop_e = threading.Event()
        self.do_stop_e.clear()
        sys.dont_write_bytecode = True

    @property
    def actions(self):
        return self._actions

    @property
    def modules(self):
        return self._modules

    # Main loop with two pipes
    def main_loop(self):
        """Main event loop handling CANMessages pipes, chaining the modules requested by the user."""
        while not self.do_stop_e.is_set():
            # Pipes to handle CANMessages on multiple channels.
            pipes = {}
            # Iterating sequentially over each module requested by the user in the configuration file.
            for name, module, params in self._actions:
                if not module.is_active:
                    continue  # Only handling active modules. Inactive modules are skipped.
                module.thr_block.wait(3)
                module.thr_block.clear()
                pipe_name = params['pipe']
                # If the pipe is newly created, initializ it with an empty CAN message. The CAN message will be further
                # processed by the loaded modules on the same pipe.
                if pipe_name not in pipes:
                    pipes[pipe_name] = CANSploitMessage()
                self.dprint(2, "DO EFFECT" + name)
                # Call module processing method and store the modified CAN message back to its pipe, so that next
                # module can continue processing the message.
                pipes[pipe_name] = module.do_effect(pipes[pipe_name], params)
                module.thr_block.set()

        self.dprint(2, "STOPPING...")
        # Here when STOP
        for name, module, params in self._actions:
            self.dprint(2, "stopping " + name)
            module.do_stop(params)

        self.do_stop_e.clear()
        self.dprint(2, "STOPPED")

    def call_module(self, index, params):
        """Call a module id `index` with the parameters supplied.

        :param int index: The index of the module to call, in the list of enabled modules.
        :param str params: The parameters to pass to the madule.

        :return: Result from the module call
        :rtype: str
        """
        if index < 0 or index >= len(self._actions):
            return 'Module {} not found!'.format(index)
        return self._actions[index][1].raw_write(params)

    def engine_exit(self):
        """Exit CANToolz engine by exiting all the loaded modules."""
        for name, module, params in self._actions:
            self.dprint(2, "exit for " + name)
            module.do_exit(params)

    def start_loop(self):
        """Start engine loop.

        :return: Status of the engine
        :rtype: bool
        """
        self.dprint(2, "START SIGNAL")
        if self._stop.is_set() and not self.do_stop_e.is_set():
            self.do_stop_e.set()
            for name, module, params in self._actions:
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

    def stop_loop(self):
        """Stop the engine.

        :return: Status of the engine
        :rtype: bool
        """
        self.dprint(2, "STOP SIGNAL")
        if not self._stop.is_set() and not self.do_stop_e.is_set():
            self.do_stop_e.set()
            while self.do_stop_e.is_set():
                time.sleep(0.01)

        self._stop.set()
        return not self._stop.is_set()

    @property
    def status_loop(self):
        """Get the status of the engine.

        :return: Status of the engine
        :rtype: bool
        """
        return not self._stop.is_set()

    # FIXME: This is not thread safe. The id returned could be wrong as soon as it is looked up.
    def find_module(self, module):
        """Find the index of the module `module` in the list of actions.

        :param str module: Module name to find

        :return: Index of the module `mod` in the list of enabled modules. -1 if not found.
        :rtype: int
        """
        index = 0
        for name, _, _ in self._actions:
            if name == module:
                break
            index += 1
        else:
            return -1  # Module not found
        return index

    def edit_module(self, index, params):
        """Edit the module configuration with new parameters.

        :param int index: Index of the module in the list of enabled modules.
        :param dict params: New parameters for the module.

        :return: Return True in case of success, False otherwise.
        :rtype: int
        """
        if index < 0 or index >= len(self._actions):
            return False
        self._actions[index][2] = self._validate_action_params(params)
        return True

    def load_config(self, fullpath):
        """Load CANToolz scenario configuration from `fullpath`.

        :param str fullpath: Fullpath to the CANToolz configuration file.

        :raises ModuleNotFoundError: When the configuration file cannot be found.
        """
        path, filename = os.path.split(fullpath)
        if not path:  # Configuration is loaded from current directory
            path = os.getcwd()
        sys.path.append(path)

        config = __import__(os.path.splitext(filename)[0])

        if hasattr(config, 'modules'):
            modules = config.modules.items()
        elif hasattr(config, 'load_modules'):
            logging.warning('The configuration `load_modules` has been deprecated in favor of `modules`.')
            modules = config.load_modules.items()
        for module, init_params in modules:
            self._init_module(module, init_params)

        for action in config.actions:
            for module, parameters in action.items():
                validated_parameters = self._validate_action_params(parameters)
                self._actions.append([module, self._modules[module], validated_parameters])

    def _init_module(self, mod, params):
        """Dynamically initialize a module.

        Dynamically find and load the module from `modules/`. If the module is not found under `modules/`, then it
        recursively looks inside the subdirectories under `modules/`. If the module name contains the subdirectory
        where to find it, it will search specifically in the specified directory and fallback to the subdirectories
        within that directory.

        .. note::

            The module must contain a class with the same name as the module itself. For instance, module `my_Module`
            must contain a class named `my_Module`

        :param str mod: Name of the module to dynamically load.
        :param list params: Parameters to pass to the module class when instanciating the module class.

        :raises: ImportError when the module cannot be found.

        """
        # Is the module name containing any '/'? Then it might indicate a subdirectory as well.
        subdir = ''
        if os.sep in mod:
            subdir, mod = mod.rsplit(os.sep, 1)
        search_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules'))
        search_path = os.path.join(search_path, subdir)
        mod_name = mod.split('~')[0]
        # Now ready to dynamically search the module.
        try:
            loaded_module = imp.load_module(mod_name, *imp.find_module(mod_name, path=[search_path]))
            logging.info('Loaded {} from directory {}'.format(mod_name, search_path))
        except ImportError:
            # Now have to try to find module in subdirectories.
            for subdir in os.listdir(search_path):
                if os.path.isdir(os.path.join(os.path.abspath(search_path), subdir)):
                    try:
                        new_search_path = os.path.join(search_path, subdir)
                        loaded_module = imp.load_module(mod_name, *imp.find_module(mod_name, path=[new_search_path]))
                        logging.info('Loaded {} from subdirectory {}'.format(mod_name, new_search_path))
                        break
                    except ImportError:
                        continue
            else:  # No module found anywhere under modules/*
                raise ImportError('Could not find {}, even in subdirectories...'.format(mod_name))
        # Dynamically instanciate the module class.
        self._modules[mod] = getattr(loaded_module, mod_name)(params)

    def _validate_action_params(self, params):
        """Validate the required parameters for an action.

        :param dict params: Parameters to validate.

        :return: Validated parameters.
        :rtype: dict
        """
        if 'pipe' not in params:
            params['pipe'] = 1
        return params
