import copy

from cantoolz.module import CANModule


class anti_theft_1(CANModule):

    name = "CAN AntiTeft system  for vircar"
    help = """

    This module emulating ANtiTeft system for CANtoolz VIRcar.

    Init params (example):
    {
        'filter': [0x71],
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
        self._try = 0
        self.can_frm = []

    def do_stop(self, params):
        self._current = 1  # 1 - blocked, 2 - ALERT, 3 - authenticated
        self._curr_auth = []
        self._try = 0
        self.can_frm = []

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):

        # FILTER MITM

        if args.get('action', '') == 'read' and can_msg.CANData and can_msg.CANFrame.frame_id not in self._status2.get('filter', []):

            if can_msg.CANFrame.get_text() in list(self._status2.get('commands', {}).keys()) and self._current == 1 and args.get('action', '') == 'read':
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

            can_msg.CANData = False  # BLOCK
            self.can_frm.append(copy.deepcopy(can_msg.CANFrame))

        elif args.get('action', '') == 'read' and can_msg.CANData and can_msg.CANFrame.frame_id in self._status2.get('filter', []) and self._current == 3:
            can_msg.CANData = False  # BLOCK
            self.can_frm.append(copy.deepcopy(can_msg.CANFrame))
        elif args.get('action', '') == 'read' and can_msg.CANData and can_msg.CANFrame.frame_id in self._status2.get('filter', []) and self._current != 3:
            can_msg.CANData = False  # BLOCK
        elif not can_msg.CANData and len(self.can_frm) > 0 and args.get('action', '') == 'write':
            can_msg.CANData = True
            can_msg.CANFrame = copy.deepcopy(self.can_frm.pop(0))

        return can_msg
