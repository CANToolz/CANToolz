"""
######################################################
#                                                    # 
#          Yet Another Car Hacking Tool              #
#                   YACHT                            #
######################################################
#      Main Code Monkey    Alyosha Sintsov           #
#                              aka @asintsov         #
#      alex.sintsov@gmail.com                        #
######################################################
#                                                    #
# Want to be there as contributor?                   #
# Help us here: https://github.com/eik00d/CANToolz   #
#                                                    #
########### MAIN CONTRIBUTORS ########################
# - Boris Ryutin ( @dukebarman )                     #
#      Fist supporter and awesome guy                #
#                                                    #
#                                                    #
# - Sergey Kononenko ( @kononencheg )                #
#        Best developer, front-end ninja             #
######################################################
# We need:                                           #
#    - more hardware to support                      #
#    - unit tests                                    # 
#    - new modules!                                  #
#    - testers!                                      #
#    - doc writes                                    #
#    - bug fixers 8)                                 #
#                                                    #
#    With support of DEF CON RUSSIA                  #
#    https://defcon-russia.ru                        #
#                                                    #
######################################################
"""

import re
import sys
import ast

from argparse import ArgumentParser

from cantoolz.engine import CANSploit
from cantoolz.webui.api import app


# Console calss
class UserInterface:
    def __init__(self):
        parser = ArgumentParser(usage='%(prog)s [options]')

        parser.add_argument('--debug', '-d', action='store', dest='DEBUG', type=int, help='Debug level')
        parser.add_argument('--config', '-c', action='store', dest='CONFIG', type=str,
                            help='Load config from file')
        parser.add_argument('--gui', '-g', action='store', dest='GUI', type=str,
                            help='GUI mode, c - console or w - web')
        parser.add_argument('--host', dest='HOST', type=str, help='Host for the web interface')
        parser.add_argument('--port', '-p', action='store', dest='PORT', type=int,
                            help='Port for web interface')

        options = parser.parse_args()

        if options.DEBUG:
            self.DEBUG = options.DEBUG
        else:
            self.DEBUG = 0

        if options.HOST:
            self.HOST = options.HOST
        else:
            self.HOST = '127.0.0.1'

        if options.PORT:
            self.PORT = options.PORT
        else:
            self.PORT = 4444

        if options.CONFIG:
            self.CONFIG = options.CONFIG
        else:
            self.CONFIG = None

        if options.GUI:
            self.GUI = options.GUI
        else:
            self.GUI = "console"

        self.CANEngine = CANSploit()

        if self.CONFIG:
            self.CANEngine.load_config(self.CONFIG)

        if self.GUI[0] == "c":
            print((self.CANEngine.ascii_logo_c))
            self.console_loop()
        elif self.GUI[0] == "w":
            self.web_loop(host=self.HOST, port=self.PORT)
        else:
            print("No such GUI...")

    def loop_exit(self):
        exit()

    def web_loop(self, host='127.0.0.1', port=4444):
        print((self.CANEngine.ascii_logo_c))
        print('CANtoolz WEB started and bound to: http://{0}:{1}'.format(host, port))
        print("\tTo exit CTRL-C...")
        app.can_engine = self.CANEngine
        try:
            app.run(host=host, port=port)
        except KeyboardInterrupt:
            print("Please wait... (do not press ctr-c again!)")
            self.CANEngine.stop_loop()
            self.CANEngine.engine_exit()
            print("gg bb")
            exit()

    def console_loop(self):
        while True:
            try:
                input_ = input(">> ")
            except KeyboardInterrupt:
                input_ = "stop"

            if input_ == 'q' or input_ == 'quit':
                print("Please wait... (do not press ctr-c again!)")
                self.CANEngine.stop_loop()
                self.CANEngine.engine_exit()
                print("gg bb")
                self.loop_exit()
            elif input_ == 'start' or input_ == 's':
                self.CANEngine.start_loop()

            elif input_ == 'stop' or input_ == 's':
                self.CANEngine.stop_loop()

            elif input_ == 'view' or input_ == 'v':
                print("Loaded queue of modules: ")
                modz = self.CANEngine.get_modules_list()
                total = len(modz)
                i = 0
                print()
                for name, module, params in modz:
                    tab1 = "\t"
                    tab2 = "\t"
                    tab1 += "\t" * int(12 / len(str(name)))
                    tab2 += "\t"
                    print(("(" + str(i) + ")\t-\t" + name + tab1 + str(params) + tab2 + "Enabled: " + str(module.is_active)))
                    if i < total - 1:
                        print("\t\t||\t")
                        print("\t\t||\t")
                        print("\t\t\/\t")
                    i += 1
                print()

            elif input_[0:5] == 'edit ' or input_[0:2] == 'e ':  # edit params from the console
                match = re.match(r"(edit|e)\s+(\d+)\s+(.+)", input_, re.IGNORECASE)
                if match:
                    module = int(match.group(2).strip())
                    _paramz = match.group(3).strip()
                    try:
                        paramz = ast.literal_eval(_paramz)
                        self.CANEngine.edit_module(module, paramz)
                        print(("Edited module: " + str(self.CANEngine.get_modules_list()[module][0])))
                        print(("Added  params: " + str(self.CANEngine.get_module_params(module))))

                        mode = 1 if self.CANEngine.get_modules_list()[module][1].is_active else 0
                        if mode == 1:
                            self.CANEngine.get_modules_list()[module][1].do_activate(0, 0)
                        if not self.CANEngine._stop.is_set():
                            self.CANEngine.get_modules_list()[module][1].do_stop(paramz)
                            self.CANEngine.get_modules_list()[module][1].do_start(paramz)
                        if mode == 1:
                            self.CANEngine.get_modules_list()[module][1].do_activate(0, 1)
                    except Exception as e:
                        print(("Edit error: " + str(e)))
                else:
                    print("Wrong format for EDIT command")

            elif input_[0:4] == 'cmd ' or input_[0:2] == 'c ':
                match = re.match(r"(cmd|c)\s+(\d+)\s+(.*)", input_, re.IGNORECASE)
                if match:
                    _mod = int(match.group(2).strip())
                    _paramz = match.group(3).strip()
                    if 1 == 1:
                        try:
                            text = self.CANEngine.call_module(_mod, str(_paramz))
                            print("Response: " + text)
                        except Exception as e:
                            print("CMD input_ error: " + str(e))

            elif input_[0:4] == 'help' or input_[0:2] == 'h ':

                match = re.match(r"(help|h)\s+(\d+)", input_, re.IGNORECASE)
                if match:
                    try:
                        module = int(match.group(2).strip())
                        mod = self.CANEngine.get_modules_list()[module][1]
                        print(("\nModule " + mod.__class__.__name__ + ": " + mod.name + "\n" + mod.help + "\n\nConsole commands:\n"))
                        for key, cmd in mod._cmdList.items():
                            print(("\t" + key + " " + cmd.desc_params + "\t\t - " + cmd.description + "\n"))
                    except Exception as e:
                        print(("Help error: " + str(e)))
                else:
                    print()
                    print('start\t\t\tStart sniff/mitm/fuzz on CAN buses')
                    print('stop or ctrl+c\t\tStop sniff/mitm/fuzz')
                    print('view\t\t\tList of loaded MiTM modules')
                    print('edit <index> [params]\tEdit parameters for modules')
                    print('cmd  <index> <cmd>\tSend some cmd to modules')
                    print('help\t\t\tThis menu')
                    print('help <index>\t\tHelp for module with chosen index')
                    print('quit\t\t\tClose port and exit')
                    print()


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    UserInterface()
