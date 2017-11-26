import copy

from cantoolz.module import CANModule


class ecu_switch(CANModule):

    name = "CAN Switch"
    help = """

    This module emulating CAN Switch.

    Init params (example):

    {
            'Cabin': {   # From Cabin interface
                'OBD2':[    # To OBD2 allowed next ID
                    0x81,   # Left door  status
                    0x82    # Right door status
                    ],
                },
            'Engine': {
                'OBD2': [
                    0x79,
                    0x709
                    ],
                'Cabin':[
                    0x79
                    ]
            },
            'OBD2':  {
                    'Engine':[
                        0x701
                    ],
                }
    }
    """

    _active = True

    def do_init(self, params):
        self._rules = params

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        current_rule = self._rules.get(args['pipe'], {})

        if can_msg.CANData and args['action'] == "read":  # READ
            for route_to, allowed_id in current_rule.items():
                if can_msg.CANFrame.frame_id in allowed_id:
                    buffer = self._rules[route_to].get('buffer', [])
                    buffer.append(copy.deepcopy(can_msg.CANFrame))
                    self._rules[route_to].update({'buffer': buffer})

        elif args['action'] == "write" and not can_msg.CANData:  # Write
            buffer_len = len(current_rule.get('buffer', []))
            if buffer_len > 0:
                can_msg.CANFrame = self._rules[args['pipe']]['buffer'].pop(0)
                can_msg.CANData = True
                can_msg.bus = self._bus

        return can_msg
