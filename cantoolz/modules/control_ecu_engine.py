from cantoolz.module import *
from cantoolz.uds import *
import json

class control_ecu_engine(CANModule):
    name = "RPM trigger for vircar"
    help = """

    This module emulating engine control.

    Init params (example):
    {
        'id_report': 0x79,
        'id_command': 0x71,
        'vin':'NLXXX6666CW006666',
        'start_uniq_key':'tGh&ujKnf5$rFgvc%',
        'commands': {
                'rpm_up':'01',
                'rpm_down':'02',
                'init': '',
                'stop': '00'
            }

    }

    """


    _active = True
    def do_init(self, params):
        self._status2 = params
        self._vin = self._status2.get("vin","NLXXX6666CW006666")
        self._auth = self._status2.get("start_uniq_key","tGh&ujKnf5$rFgvc%")
        self._status_engine = 0xfe # fe - unknown, ff - wrong key, 01 - turned on, 02 - dead
        self._status_rpm = 0
        self.rpm_up = 0
        self.rpm_down = 0
        self.frames = []

        self._cmdList['status'] = Command("Get engine status", 0, "", self.control_get_status, True)
        self._cmdList['rpmup'] = Command("Increase RMP", 0, "", self.control_rpm_up, True)
        self._cmdList['rpmdw'] = Command("Decrease RMP", 0, "", self.control_rpm_down, True)
        self._cmdList['start'] = Command("Start engine", 0, "", self.control_start_engine, True)
        self._cmdList['stop'] = Command("Stop engine", 0, "", self.control_stop_engine, True)

    def control_rpm_up(self, flag):
        self.frames.append(CANMessage(self._status2['id_command'],2,bytes.fromhex(self._status2['commands']['rpm_up'] + '20'),False, CANMessage.DataFrame))
        return ""

    def control_rpm_down(self, flag):
        self.frames.append(CANMessage(self._status2['id_command'],2,bytes.fromhex(self._status2['commands']['rpm_down'] + '20'),False, CANMessage.DataFrame))
        return ""

    def control_start_engine(self, flag):
        i = 0
        key_x = ""
        for byte_k in self._vin:
            key_x += chr(ord(byte_k) ^ ord(self._auth[i]))  # XOR with KEY (to get VIN)
            i += 1

        self.frames.extend(ISOTPMessage.generate_can(self._status2['id_command'], [ord(byt) for byt in list(key_x)] ))
        return ""

    def control_stop_engine(self, flag):
        self.frames.append(CANMessage(self._status2['id_command'],1 , bytes.fromhex(self._status2['commands']['stop']),False, CANMessage.DataFrame))
        return ""

    def control_get_status(self, flag):
        st = "Turned OFF"
        if self._status_engine  == 0x03:
            st = "Turned OFF"
        elif self._status_engine  == 0xff:
            st = "Turned OFF, start failed (auth)"
        elif self._status_engine  == 0x01:
            st = "Turned ON"
        elif self._status_engine  == 0x02:
            st = "Stalled"

        json_string = json.dumps({'status': self._status_engine, 'text': st, 'rpm': self._status_rpm})

        return json_string

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if args['action'] == 'read' and can_msg.CANData: # READ
            if can_msg.CANFrame.frame_id == self._status2.get('id_report', 0xffff) and can_msg.CANFrame.frame_length == 3:
                self._status_rpm = struct.unpack(">H", can_msg.CANFrame.frame_raw_data[1:3])[0] # Read RMP
                self._status_engine = can_msg.CANFrame.frame_data[0] # Read Engine status
            elif can_msg.CANFrame.frame_id == self._status2.get('id_report', 0xffff) and can_msg.CANFrame.frame_length == 2 and can_msg.CANFrame.frame_data[0] == 0xff:
                self._status_engine = can_msg.CANFrame.frame_data[1]
        if args['action'] == 'write' and not can_msg.CANData:
            if len(self.frames) > 0:
                can_msg.CANFrame = self.frames.pop(0)
                can_msg.CANData = True
                can_msg.bus = self._bus
        return can_msg
