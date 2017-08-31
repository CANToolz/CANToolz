import re
import ast
import cmd
import traceback


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
        """View table of the loaded actions."""
        actions = self.can_engine.actions
        print('Loaded queue of actions (total {}):'.format(len(actions)), end='\n' * 2)
        # Generate table rows
        table = [
            ['({})'.format(i), name, str(params), str(module.is_active)]
            for i, (name, module, params) in enumerate(actions)]
        # Create printing format with correct max padding.
        sizes = [10] * 4  # Padding 10 characters minimum.
        for row in table:
            # Get max(len(cell), padding) for each cell in each row of the table
            sizes = list(map(max, zip(map(len, row), sizes)))
        row_format = ''.join('{{:{}}}'.format(size + 4) for size in sizes)

        print(row_format.format(*('ID', 'Module', 'Parameters', 'Active')))
        print('-' * (sum(sizes) + 2 * len(sizes)))
        if len(table):
            for row in table[:-1]:
                print(row_format.format(*row))
                print(row_format.format(*('', '||', '', '', '')))
                print(row_format.format(*('', '||', '', '', '')))
                print(row_format.format(*('', '\/', '', '', '')))
            print(row_format.format(*table[-1]), end='\n' * 2)

    def do_edit(self, arg):
        """Edit parameters for a module.

        edit <module id> <configuration dictionary>

        Example:
            edit 0 {'action': 'write', 'pipe': 'Cabin'}
        """
        match = re.match(r'(\d+)\s+(.+)', arg, re.IGNORECASE)
        if not match:
            print('Missing/invalid required parameters. See: help edit')
            return
        module = int(match.group(1).strip())
        _paramz = match.group(2).strip()
        try:
            paramz = ast.literal_eval(_paramz)
            self.can_engine.edit_module(module, paramz)
        except Exception:
            print('Error when edit the module with {}:'.format(arg))
            traceback.print_exc()
            return
        print('Edited module: {}'.format(self.can_engine.actions[module][0]))
        print('Added params: {}'.format(self.can_engine.actions[module][2]))

        active = self.can_engine.actions[module][1].is_active
        if active:
            self.can_engine.actions[module][1].do_activate(0, 0)
        if self.can_engine.status_loop:
            self.can_engine.actions[module][1].do_stop(paramz)
            self.can_engine.actions[module][1].do_start(paramz)
        if active:
            self.can_engine.actions[module][1].do_activate(0, 1)

    def do_cmd(self, arg):
        """Call module command.

        cmd <module id> <cmd>

        Example:
            cmd 0 S
        """
        match = re.match(r'(\d+)\s+(.*)', arg, re.IGNORECASE)
        if not match:
            print('Missing/invalid required parameters. See: help cmd')
            return
        _mod = int(match.group(1).strip())
        _paramz = match.group(2).strip()
        try:
            text = self.can_engine.call_module(_mod, str(_paramz))
        except Exception:
            print('Error when calling the command {}:'.format(arg))
            traceback.print_exc()
            return
        print('Response: {}'.format(text))

    def do_help(self, arg):
        """Show module help or CANToolz help if no parameter specified.

        help [module id]
        """
        match = re.match(r'(\d+)', arg, re.IGNORECASE)
        if not match:
            super(CANToolzCLI, self).do_help(arg)
            return
        module = int(match.group(1).strip())
        try:
            mod = self.can_engine.actions[module][1]
        except Exception:
            print('Error when retrieving the requested module: ')
            traceback.print_exc()
            return
        print('Module {}: {}\n{}\nCommands:'.format(mod.__class__.__name__, mod.name, mod.help))
        for key, value in mod.commands.items():
            print('\t{} {} - {}'.format(key, value.desc_params, value.description))
        print()

    def do_quit(self, arg):
        """Quit CANToolz"""
        print('Exiting CANToolz. Please wait... ', end='')
        self.can_engine.stop_loop()
        self.can_engine.engine_exit()
        print('Done')
        raise SystemExit
