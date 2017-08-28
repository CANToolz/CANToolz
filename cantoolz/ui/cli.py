import re
import ast


class CANToolzCLI:

    def __init__(self, can_engine):
        self.can_engine = can_engine

    def loop_exit(self):
        exit()

    def run(self):
        while True:
            try:
                input_ = input(">> ")
            except KeyboardInterrupt:
                input_ = "stop"

            if input_ == 'q' or input_ == 'quit':
                print("Please wait... (do not press ctr-c again!)")
                self.can_engine.stop_loop()
                self.can_engine.engine_exit()
                print("gg bb")
                self.loop_exit()
            elif input_ == 'start' or input_ == 's':
                self.can_engine.start_loop()

            elif input_ == 'stop' or input_ == 's':
                self.can_engine.stop_loop()

            elif input_ == 'view' or input_ == 'v':
                print("Loaded queue of modules: ")
                modz = self.can_engine.get_modules_list()
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
                        self.can_engine.edit_module(module, paramz)
                        print(("Edited module: " + str(self.can_engine.get_modules_list()[module][0])))
                        print(("Added  params: " + str(self.can_engine.get_module_params(module))))

                        mode = 1 if self.can_engine.get_modules_list()[module][1].is_active else 0
                        if mode == 1:
                            self.can_engine.get_modules_list()[module][1].do_activate(0, 0)
                        if not self.can_engine._stop.is_set():
                            self.can_engine.get_modules_list()[module][1].do_stop(paramz)
                            self.can_engine.get_modules_list()[module][1].do_start(paramz)
                        if mode == 1:
                            self.can_engine.get_modules_list()[module][1].do_activate(0, 1)
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
                            text = self.can_engine.call_module(_mod, str(_paramz))
                            print("Response: " + text)
                        except Exception as e:
                            print("CMD input_ error: " + str(e))

            elif input_[0:4] == 'help' or input_[0:2] == 'h ':

                match = re.match(r"(help|h)\s+(\d+)", input_, re.IGNORECASE)
                if match:
                    try:
                        module = int(match.group(2).strip())
                        mod = self.can_engine.get_modules_list()[module][1]
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
