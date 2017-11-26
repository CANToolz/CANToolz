import os
import sys
import glob
import time
import logging
import threading
import collections

from importlib.machinery import SourceFileLoader

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

    def __init__(self, path_modules=None):
        # List of actions with their parameters to perform during the scenario.
        self._actions = []
        # Dictionary of initialized modules for the scenario.
        self._modules = {}
        # Path to the CANToolz modules directory.
        self._path_modules = path_modules
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

    def _get_load_paths(self):
        """Creates the paths where to look for modules based on CANToolz's strategy.

        :return: List of paths where to start looking for modules
        :rtype: list
        """
        strats = []
        # See: https://github.com/CANToolz/CANToolz/issues/16
        # 1. From user specified directory
        if self._path_modules:
            strats.append(self._path_modules)
        # 2. From dotfile directory
        strats.append(os.path.join(os.path.expanduser('~'), '.cantoolz', 'modules'))
        # 3. From package directory (stock modules)
        strats.append(os.path.join(os.path.dirname(__file__), 'modules'))
        return strats

    def list_modules(self):
        """List the available modules that can be loaded by the user.

        :return: Dictionaries of module, with {name: description} for each module existing.
        :rtype: collections.OrderedDict
        """
        modules = collections.OrderedDict()
        # Searching modules in reversed strategy so that user specified modules override stock modules
        for search_path in self._get_load_paths()[::-1]:
            search_path = os.path.join(search_path, '**', '*.py')
            for fullpath in glob.iglob(search_path, recursive=True):
                if fullpath.endswith('__init__.py'):
                    continue
                path, filename = os.path.split(fullpath)
                subdir = os.path.split(os.path.dirname(fullpath))[1]  # Get the one-level up directory
                filename = os.path.splitext(filename)[0]
                sys.path.append(path)
                module = __import__(filename)
                if subdir != 'modules':  # If the module is under a subdirectory (e.g. io, vircar)
                    new_module = {os.path.join(subdir, filename): (getattr(module, filename).name, path)}
                else:
                    new_module = {filename: (getattr(module, filename).name, path)}
                modules.update(new_module)
        return modules

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
        else:
            raise AttributeError("Missing 'modules' attribute in your configuration '{}'.".format(filename))

        for module, init_params in modules:
            for path in self._get_load_paths():
                if not os.path.exists(path):
                    continue
                try:
                    logging.debug('Searching module {} from {}'.format(module, path))
                    self._init_module(path, module, init_params)
                    break
                except ImportError:
                    logging.debug('Module {} not found in {}'.format(module, path))
                    continue
            else:
                raise ImportError(
                    "Could not find the module named '{}'. Check that your configuration '{}' is valid.".format(module, filename))

        for action in config.actions:
            for module, parameters in action.items():
                validated_parameters = self._validate_action_params(parameters)
                self._actions.append([module, self._modules[module], validated_parameters])

    def _init_module(self, path, mod, params):
        """Dynamically initialize a module.

        Dynamically find and load the module from `modules/`. If the module is not found under `modules/`, then it
        recursively looks inside the subdirectories under `modules/`. If the module name contains the subdirectory
        where to find it, it will search specifically in the specified directory and fallback to the subdirectories
        within that directory.

        .. note::

            The module must contain a class with the same name as the module itself. For instance, module `my_Module`
            must contain a class named `my_Module`

        :param str path: Path to the modules directory from where to load the modules.
        :param str mod: Name of the module to dynamically load.
        :param list params: Parameters to pass to the module class when instanciating the module class.

        :raises: ImportError when the module cannot be found.

        """
        # Is the module name containing any '/'? Then it might indicate a subdirectory as well.
        subdir = ''
        if os.sep in mod:
            subdir, mod = mod.rsplit(os.sep, 1)
        # TODO: Find a nicer way to handle configuration containing '/' under Windows
        if not subdir and '/' in mod:
            subdir, mod = mod.rsplit('/', 1)
        search_path = os.path.abspath(path)
        search_path = os.path.join(search_path, subdir)
        if not os.path.exists(search_path):
            raise ImportError('Could not import module. Path {} does not exist...'.format(search_path))
        mod_name = mod.split('~')[0]
        # Now ready to dynamically search the module.
        try:
            loaded_module = SourceFileLoader(mod_name, os.path.join(search_path, mod_name + '.py')).load_module()
            logging.info('Loaded {} from directory {}'.format(mod_name, search_path))
        except FileNotFoundError:  # Module not found in directory; let's try subdirectories now.
            for subdir in os.listdir(search_path):
                if os.path.isdir(os.path.join(os.path.abspath(search_path), subdir)):
                    new_search_path = os.path.join(search_path, subdir)
                    try:
                        loaded_module = SourceFileLoader(mod_name, os.path.join(new_search_path, mod_name + '.py')).load_module()
                        logging.info('Loaded {} from subdirectory {}'.format(mod_name, new_search_path))
                        break  # Module found in a subdirectory; no need to look further.
                    except FileNotFoundError:
                        continue
            else:  # Module could not be found in any subdirectories; giving up now.
                raise ImportError('Could not find {}, even in subdirectories...'.format(mod_name))
        # Dynamically instanciate the module class.
        self._modules[mod] = getattr(loaded_module, mod_name)(params)

    @staticmethod
    def _validate_action_params(params):
        """Validate the required parameters for an action.

        :param dict params: Parameters to validate.

        :return: Validated parameters.
        :rtype: dict
        """
        if 'pipe' not in params:
            params['pipe'] = 1
        return params
