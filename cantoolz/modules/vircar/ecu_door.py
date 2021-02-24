import time

from cantoolz.can import CANMessage
from cantoolz.module import CANModule


class ecu_door(CANModule):

    name = "CAN ECU for the car door"
    help = """

    This module emulating car's door.

    Init params (example):

    {
            'id_report': 0x91,
            'id_command': 0x81,
            'commands': {
                'lock':'1000',
                'unlock':'10FF',
                'init': '00FF',
            },

            'reports': {
                'Locked': '2000',
                'Unlocked': '20FF'
            },
            'reports_delay': 1.2
    }

    """

    _active = True

    def do_init(self, params):
        self._params = params
        self._params['status'] = 'Locked'
        self._frames = []
        self._last_sent = time.process_time()

    def do_start(self, params):
        self._params['status'] = 'Locked'

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if args['action'] == 'read' and can_msg.CANData:  # READ
            if self._params['id_command'] == can_msg.CANFrame.frame_id:
                for cmd, value in self._params['commands'].items():
                    len_cmd = int(len(value) / 2)
                    if can_msg.CANFrame.frame_length == len_cmd and can_msg.CANFrame.frame_raw_data[0:len_cmd] == bytes.fromhex(value):
                            if cmd == 'lock':
                                self._params['status'] = 'Locked'
                                self._last_sent -= self._params.get('reports_delay', 1.0)
                            if cmd == 'unlock':
                                self._params['status'] = 'Unlocked'
                                self._last_sent -= self._params.get('reports_delay', 1.0)

        elif args['action'] == 'write' and not can_msg.CANData and self._params['status'] != 'Turned off':  # Write
            if (time.process_time() - self._last_sent) >= self._params.get('reports_delay', 1.0):
                can_msg.CANFrame = CANMessage(
                    self._params.get('id_report', 0xffff),
                    len(self._params.get('reports', {}).get(self._params['status'], '')) / 2,
                    bytes.fromhex(self._params.get('reports', {}).get(self._params['status'], '0000')), False,
                    CANMessage.DataFrame
                )
                can_msg.CANData = True
                can_msg.bus = self._bus
                self._last_sent = time.process_time()

        return can_msg
