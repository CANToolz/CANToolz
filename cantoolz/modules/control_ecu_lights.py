from cantoolz.module import *
from cantoolz.uds import *
import json

class control_ecu_lights(CANModule):
    name = "Lights trigger for vircar"
    help = """

    This module emulating lightsl.

    Init params (example):
    {
        'id_report': {0x111:'Left', 0x112:'Right'},
            'id_command': 0x101,
            'commands': {
                'on':'01',
                'off':'00',
                'distance': '02',
            },

            'reports': {
                'LIGHTS ON': 'ff0101',
                'DISTANCE LIGHTS ON': 'ff0202',
                'Lights OFF': '000000'
            }
    }

    """


    _active = True
    def do_init(self, params):
        self._status2 = params
        self.frames = []
        self._doors = {}
        self._cmdList['status'] = Command("Get lights status", 0, "", self.control_get_status, True)
        self._cmdList['off'] = Command("Lights OFF", 0, "", self.lights_off, True)
        self._cmdList['on'] = Command("Lights ON", 0, "", self.lights_on, True)
        self._cmdList['distance'] = Command("Disatnace lights on", 0, "", self.dlights_on, True)

    def lights_off(self, flag):
        self.frames.append(CANMessage(self._status2['id_command'],int(len(self._status2['commands']['off'])/2),bytes.fromhex(self._status2['commands']['off']),False, CANMessage.DataFrame))
        return ""

    def lights_on(self, flag):
        self.frames.append(CANMessage(self._status2['id_command'],int(len(self._status2['commands']['on'])/2),bytes.fromhex(self._status2['commands']['on']),False, CANMessage.DataFrame))
        return ""

    def dlights_on(self, flag):
        self.frames.append(CANMessage(self._status2['id_command'],int(len(self._status2['commands']['distance'])/2),bytes.fromhex(self._status2['commands']['distance']),False, CANMessage.DataFrame))
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
