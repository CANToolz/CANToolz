from cantoolz.module import *
from cantoolz.uds import *
import json

class control_ecu_doors(CANModule):
    name = "Doors trigger for vircar"
    help = """

    This module emulating lock control.

    Init params (example):
    {
        'id_report': {0x91:'Left', 0x92:'Right'},
            'id_command': 0x81,
            'commands': {
                'lock':'1000',
                'unlock':'10ff',
                'init': '00ff',
            },

            'reports': {
                'Locked': '2000',
                'Unlocked': '20ff'
            }
    }

    """


    _active = True
    def do_init(self, params):
        self._status2 = params
        self.frames = []
        self._doors = {}
        self._cmdList['status'] = Command("Get doors status", 0, "", self.control_get_status, True)
        self._cmdList['central_lock'] = Command("Lock doors", 0, "", self.control_lock, True)
        self._cmdList['central_unlock'] = Command("Unlock doors", 0, "", self.control_unlock, True)

    def control_lock(self, flag):
        self.frames.append(CANMessage(self._status2['id_command'],int(len(self._status2['commands']['lock'])/2),bytes.fromhex(self._status2['commands']['lock']),False, CANMessage.DataFrame))
        return ""

    def control_unlock(self, flag):
        self.frames.append(CANMessage(self._status2['id_command'],int(len(self._status2['commands']['unlock'])/2),bytes.fromhex(self._status2['commands']['unlock']),False, CANMessage.DataFrame))
        return ""

    def control_get_status(self, flag):
        json_string = json.dumps({'status': self._doors})

        return json_string

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if args['action'] == 'read' and can_msg.CANData: # READ
            if can_msg.CANFrame.frame_id in self._status2.get('id_report', {}).keys():
                for status, code in self._status2['reports'].items():
                    if can_msg.CANFrame.frame_length == int(len(code)/2) and code == self.get_hex(can_msg.CANFrame.frame_raw_data):
                        self._doors.update(
                            {self._status2['id_report'][can_msg.CANFrame.frame_id]: status}
                        )

        if args['action'] == 'write' and not can_msg.CANData:
            if len(self.frames) > 0:
                can_msg.CANFrame = self.frames.pop(0)
                can_msg.CANData = True
                can_msg.bus = self._bus
        return can_msg
