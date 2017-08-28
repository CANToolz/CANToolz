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

import sys

from argparse import ArgumentParser

from cantoolz.engine import CANSploit
from cantoolz.ui.cli import CANToolzCLI
from cantoolz.ui.web import app


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
            self.console_loop()
        elif self.GUI[0] == "w":
            self.web_loop(host=self.HOST, port=self.PORT)
        else:
            print("No such GUI...")

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
        print((self.CANEngine.ascii_logo_c))
        cli = CANToolzCLI(self.CANEngine)
        cli.run()


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    UserInterface()
