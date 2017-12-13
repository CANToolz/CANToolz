import time

from cantoolz.replay import Replay
from cantoolz.module import CANModule, Command


class replay(CANModule):

    name = "Replay module"
    help = """

    This module allows loading/saving CAN messages for replay.

    Init parameters:
        - 'load_from': 'filename'  # Load packets from file (optional)
        - 'save_to': 'filename'    # Save to file (mod_replay.save by default)

    Module parameters: none
        - 'delay': 0               # Delay in second between each frame (0 by default)
        - 'ignore_time': False     # Ignore the CAN message timestamps during replay

    Example:
        {'delay': .2}

    """

    filename = None

    _active = True
    version = 1.0

    is_replaying = False
    is_sniffing = False

    def get_status(self):
        status = 'Current status: {}\n'.format(self._active)
        status += 'Sniffing is: {}\n'.format(self.is_sniffing)
        status += 'Replaying is: {}\n'.format(self.is_replaying)
        status += 'CAN frames in memory: {}\n'.format(len(self.replay))
        status += 'CAN frames in queue: {}'.format(self._num2 - self._num1)
        return status

    def cmd_load(self, filename):
        """Load CAN messages from a file.

        :param str filename: Filename containing the CAN messages to load.
        """
        try:
            self.replay.parse_file(filename, self._bus)
            self.dprint(1, 'Loaded {} CAN frames.'.format(len(self.replay)))
        except Exception as e:
            self.dprint(0, "Cannot open '{}' when trying to load CAN messages: {}".format(filename, e))
        return 'Loaded {} CAN frames.'.format(len(self.replay))

    def do_init(self, params):
        self.replay = Replay()
        self.last = time.clock()
        self._last = 0
        self._full = 1
        self._num1 = 0
        self._num2 = 0
        self.filename = params.get('save_to', 'replay.save')

        if 'load_from' in params:
            self.cmd_load(params['load_from'])

        self.commands['g'] = Command("Enable/Disable sniffing to collect CAN packets", 0, "", self.cmd_sniff, True)
        self.commands['p'] = Command("Print count of loaded CAN packets", 0, "", self.cmd_show_count, True)
        self.commands['l'] = Command("Load CAN packets from file", 1, " <file> ", self.cmd_load, True)
        self.commands['r'] = Command("Replay range from loaded CAN packets, from X to Y (numbers)", 1, " <X>-<Y> ", self.cmd_replay_range, True)
        self.commands['d'] = Command("Save range of loaded CAN packets, from X to Y (numbers)", 1, " <X>-<Y>, <filename>", self.cmd_save_dump, True)
        self.commands['c'] = Command("Reset loaded CAN packets", 0, "", self.cmd_reset, True)

    def cmd_reset(self):
        """Reset the replay session back to nothing."""
        self.replay = Replay()
        self._last = 0
        self._full = 1
        self._num1 = 0
        self._num2 = 0
        return 'Replay buffer has been reset!'

    def cmd_save_dump(self, params):
        """Save a range of CAN messages from the loaded packets.

        :param str params: Indexes of the first and last CAN message to replay; filename where to store the frames.
        """
        filename = self.filename
        indexes, *chunks = map(str.strip, params.split(','))
        if len(chunks) == 1:
            filename = chunks[0]
        try:
            start, end = map(int, indexes.split('-'))
        except ValueError:
            start = 0
            end = len(self.replay)
        return self.replay.save_dump(filename, start, end - start)

    def cmd_sniff(self):
        """Enable/Disable sniffing on the CAN bus."""
        self.is_replaying = False

        # Toggle sniffing to False.
        if self.is_sniffing:
            self.is_sniffing = False
            self.commands['r'].is_enabled = True
            self.commands['d'].is_enabled = True
        # Toggle sniffing to True.
        else:
            self.is_sniffing = True
            self.commands['r'].is_enabled = False
            self.commands['d'].is_enabled = False
            self.replay.restart_time()
        return 'Sniffing is now: {}'.format(self.is_sniffing)

    def cmd_replay_range(self, indexes=None):
        """Replay a range of CAN messages from the loaded frames.

        :param str indexes: Indexes of the first and last CAN message to replay.
        """
        self.is_replaying = False
        self.is_sniffing = False
        if indexes is None:
            indexes = '0-{}'.format(len(self.replay))
        try:
            self._num1, self._num2 = map(int, indexes.split('-'))
            if 0 <= self._num1 < self._num2 <= len(self.replay):
                self.is_replaying = True
                self._full = self._num2 - self._num1
                self._last = 0
                self.commands['g'].is_enabled = False
                self.replay.set_index(self._num1)
        except ValueError:
            self.is_replaying = False

        return "Replay mode changed to: " + str(self.is_replaying)

    def cmd_show_count(self):
        """Show the number of loaded CAN messages."""
        return 'Loaded packets: {}'.format(len(self.replay))

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can, args):
        if self.is_sniffing and can.data is not None:
            self.replay.append(can)
        elif self.is_replaying and can.data is None:
            d_time = float(args.get('delay', 0))
            ignore = bool(args.get('ignore_time', False))
            try:
                next_can = self.replay.next(d_time, ignore)
                if next_can and next_can.data is not None:
                    can = next_can
                    self._num1 += 1
                    self._last += 1
                can.bus = self._bus
                self._status = self._last / (self._full / 100.0)
            # TODO: Use less broad exception.
            except Exception:
                self.is_replaying = False
                self.commands['g'].is_enabled = True
                self.replay.reset()
            if self._num1 == self._num2:
                self.is_replaying = False
                self.commands['g'].is_enabled = True
                self.replay.reset()
        return can
