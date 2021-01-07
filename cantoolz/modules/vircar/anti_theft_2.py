import time

from cantoolz.can import CANMessage
from cantoolz.module import CANModule


class anti_theft_2(CANModule):

    name = "CAN AntiTeft system  for vircar"
    help = """

    This module emulating ANtiTeft system for CANtoolz VIRcar.

    Init params (example):
    {
        'stop_engine': '0x71:1:00',
        'filter':[0x71],
        'commands': {
                '0x101:1:01':'one',
                '0x101:1:02':'two',
                '0x101:1:00':'three'
            },
        'pass_seq':['one','one','two','one','three','two','three'] # Passcode sequence
    }

    """

    _active = True

    def do_init(self, params):
        self._status2 = params
        self._current = 1  # 1 - blocked, 2 - ALERT, 3 - authenticated
        self._curr_auth = []
        self.stop = False
        cmds = self._status2['stop_engine'].split(':')
        self.can_stop = CANMessage(int(cmds[0], 16) if cmds[0][0:2] == '0x' else int(cmds[0]), int(cmds[1]), bytes.fromhex(cmds[2]), False, CANMessage.DataFrame)
        self._try = 0
        self.last = time.process_time()

    def do_stop(self, params):
        self._current = 1  # 1 - blocked, 2 - ALERT, 3 - authenticated
        self._curr_auth = []
        self._try = 0

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):

        if self.stop and not can_msg.CANData and time.process_time() - self.last > 1.5 and args.get('action', '') == 'write' and self._current != 3:
            can_msg.CANData = True
            can_msg.CANFrame = self.can_stop
            if self._current != 2:
                self.stop = False
            self.last = time.process_time()

        # FILTER
        elif can_msg.CANData and self._current != 3 and args.get('action', '') == 'read':
            if can_msg.CANFrame.frame_id in self._status2.get('filter', []):
                self.stop = True

            elif can_msg.CANFrame.get_text() in list(self._status2.get('commands', {}).keys()) and self._current != 2:
                ath = self._status2['commands'][can_msg.CANFrame.get_text()]
                self._curr_auth.append(ath)
                if len(self._curr_auth) < len(self._status2.get('pass_seq', ['one'])):
                    if self._curr_auth != self._status2.get('pass_seq', ['one'])[:len(self._curr_auth)]:
                        self._curr_auth = []
                        self._try += 1

                        if self._try > 3:
                            self._current = 2  # Anti bruteforce
                elif len(self._curr_auth) == len(self._status2.get('pass_seq', ['one'])):
                    if self._curr_auth == self._status2.get('pass_seq', ['one']):
                        self._current = 3
                    else:
                        self._curr_auth = []
                        self._try += 1

                        if self._try > 3:
                            self._current = 2  # Anti bruteforce

        return can_msg
