from cantoolz.uds import UDSMessage
from cantoolz.isotp import ISOTPMessage
from cantoolz.module import CANModule, Command


class uds_tester_ecu_engine(CANModule):

    name = "UDS Tester device emulator"
    help = """

    This module emulating UDS for vircar Engine ECU.

    Init params (example):
    {
        'id_uds': 0x701,
        'uds_shift': 0x08,
        'uds_key':''
    }

    """

    _active = True

    def do_init(self, params):
        self._status2 = params
        self.frames = []
        self.init_sess2 = None
        self._seed = []
        self.auth_resp_byte = 0
        self.record_status = False
        self.wait_for_auth = False

        self.commands['auth'] = Command("UDS Auth", 0, "", self.control_auth, True)
        self.commands['set_key'] = Command("Set UDS access key", 1, "<key>", self.set_key, True)
        self.commands['write_id'] = Command("Write parameter (HEX)", 1, "<ident>, <data>", self.write_param, True)

    def write_param(self, key):
        uds_msg = UDSMessage()
        (ids, data) = key.split(',')
        ids = list(bytes.fromhex(ids.strip()))
        data = list(bytes.fromhex(data.strip()))
        self.frames.extend(uds_msg.add_request(
            self._status2['id_uds'],  # ID
            0x2e,  # Service
            ids[0],  # Sub function
            ids[1:] + data))
        return ""

    def get_status(self):
        return "Current status: " + str(self._active) + "\nKEY: " + self._status2['uds_key'] + "\nResponse AUTH: " + str(self.auth_resp_byte)

    def set_key(self, key):
        self._status2.update({'uds_key': key.strip()})
        return ""

    def control_auth(self):
        uds_msg = UDSMessage()
        self.frames.extend(uds_msg.add_request(
            self._status2['id_uds'],  # ID
            0x27,  # Service
            0x1,  # Sub function
            []))
        self.wait_for_auth = True
        return ""

    def call_auth(self):
        uds_msg = UDSMessage()
        i = 0
        key = []
        for byte_k in self._status2['uds_key']:
            key.append(ord(byte_k) ^ self._seed[i % 4])
            i += 1
        self.frames.extend(uds_msg.add_request(
            self._status2['id_uds'],  # ID
            0x27,  # Service
            0x2,  # Sub function
            key))
        self.wait_for_auth = False

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if args['action'] == 'read' and can_msg.CANData and can_msg.CANFrame.frame_id == self._status2['id_uds'] + self._status2['uds_shift']:  # READ
            if not self.init_sess2:
                self.init_sess2 = ISOTPMessage(can_msg.CANFrame.frame_id)

                ret = self.init_sess2.add_can(can_msg.CANFrame)

                if ret < 0:
                    self.init_sess2 = None
                elif ret == 1:
                    uds_msg = UDSMessage()
                    uds_msg.add_raw_request(self.init_sess2)
                    if can_msg.CANFrame.frame_id in uds_msg.sessions:
                        if 0x27 + 0x40 in uds_msg.sessions[can_msg.CANFrame.frame_id]:  # Check service
                            if 1 in uds_msg.sessions[can_msg.CANFrame.frame_id][0x27 + 0x40]:  # Check sub: SEED request
                                self._seed = uds_msg.sessions[can_msg.CANFrame.frame_id][0x27 + 0x40][1]['data']
                                if self.wait_for_auth:
                                    self.call_auth()
                            elif 2 in uds_msg.sessions[can_msg.CANFrame.frame_id][0x27 + 0x40] and len(uds_msg.sessions[can_msg.CANFrame.frame_id][0x27 + 0x40][2]['data']) == 1:  # Check sub: KEY enter
                                self.auth_resp_byte = uds_msg.sessions[can_msg.CANFrame.frame_id][0x27 + 0x40][2]['data'][0]
                        elif 0x2e + 0x40 in uds_msg.sessions[can_msg.CANFrame.frame_id] and 0x55 in uds_msg.sessions[can_msg.CANFrame.frame_id][0x2e + 0x40] and uds_msg.sessions[can_msg.CANFrame.frame_id][0x2e + 0x40][0x55]['data'][0] == 0x55:
                            self.record_status = True
                        elif 0x2e + 0x40 in uds_msg.sessions[can_msg.CANFrame.frame_id] and 0x0 in uds_msg.sessions[can_msg.CANFrame.frame_id][0x2e + 0x40] and uds_msg.sessions[can_msg.CANFrame.frame_id][0x2e + 0x40][0x0]['data'][0:1] == [0x0]:                                   # data
                            self.record_status = False
                    self.init_sess2 = None

        if args['action'] == 'write' and not can_msg.CANData:
            if len(self.frames) > 0:
                can_msg.CANFrame = self.frames.pop(0)
                can_msg.CANData = True
                can_msg.bus = self._bus
        return can_msg
