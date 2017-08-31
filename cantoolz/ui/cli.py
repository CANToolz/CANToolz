import re
import ast
import cmd


class CANToolzCLI(cmd.Cmd):

    intro = 'CANToolz prompt.   Type help or ? to list commands.\n'
    prompt = '>> '

    def __init__(self, can_engine, *args, **kwargs):
        self.can_engine = can_engine
        super(CANToolzCLI, self).__init__(*args, **kwargs)

    def do_start(self, arg):
        """Start CANToolz engine."""
        print('CANToolz engine started: {}'.format(self.can_engine.start_loop()))

    def do_stop(self, arg):
        """Stop CANToolz engine."""
        print('CANToolz engine started: {}'.format(self.can_engine.stop_loop()))

    def do_view(self, arg):
        """View loaded actions."""
        print("Loaded queue of actions: ")
        modz = self.can_engine.actions
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

    def do_edit(self, arg):
        """Edit parameters for a module.

        edit <module id> <configuration dictionary>

        Example:
            edit 0 {'action': 'write', 'pipe': 'Cabin'}
        """
        match = re.match(r'(\d+)\s+(.+)', arg, re.IGNORECASE)
        if match:
            module = int(match.group(1).strip())
            _paramz = match.group(2).strip()
            try:
                paramz = ast.literal_eval(_paramz)
                self.can_engine.edit_module(module, paramz)
                print(("Edited module: " + str(self.can_engine.actions[module][0])))
                print(("Added  params: " + str(self.can_engine.actions[module][2])))

                mode = 1 if self.can_engine.actions[module][1].is_active else 0
                if mode == 1:
                    self.can_engine.actions[module][1].do_activate(0, 0)
                if not self.can_engine._stop.is_set():
                    self.can_engine.actions[module][1].do_stop(paramz)
                    self.can_engine.actions[module][1].do_start(paramz)
                if mode == 1:
                    self.can_engine.actions[module][1].do_activate(0, 1)
            except Exception as e:
                print("edit error: " + str(e))
                return
        else:
            print('Missing/invalid required parameters. See: help edit')
            return

    def do_cmd(self, arg):
        """Call module command.

        cmd <module id> <cmd>

        Example:
            cmd 0 S
        """
        match = re.match(r'(\d+)\s+(.*)', arg, re.IGNORECASE)
        if match:
            _mod = int(match.group(1).strip())
            _paramz = match.group(2).strip()
            try:
                text = self.can_engine.call_module(_mod, str(_paramz))
                print("Response: " + text)
            except Exception as e:
                print("cmd arg error: " + str(e))
                return
        else:
            print('Missing/invalid required parameters. See: help cmd')

    def do_help(self, arg):
        """Show module help or CANToolz help if no parameter specified.

        help [module id]
        """
        match = re.match(r'(\d+)', arg, re.IGNORECASE)
        if match:
            try:
                module = int(match.group(1).strip())
                mod = self.can_engine.actions[module][1]
                print(("\nModule " + mod.__class__.__name__ + ": " + mod.name + "\n" + mod.help + "\n\nConsole commands:\n"))
                for key, value in mod.commands.items():
                    print(("\t" + key + " " + value.desc_params + "\t\t - " + value.description + "\n"))
            except Exception as e:
                print(("Help error: " + str(e)))
                return
        else:
            super(CANToolzCLI, self).do_help(arg)

    def do_quit(self, arg):
        """Quit CANToolz"""
        print("Please wait... (do not press ctr-c again!)")
        self.can_engine.stop_loop()
        self.can_engine.engine_exit()
        print("gg bb")
        raise SystemExit
