from cantoolz.module import *
from cantoolz.uds import *
import time
import random

class ecu_engine(CANModule):
    name = "Engine emulator for vircar"
    help = """

    This module emulating car engine.

    Init params (example):
    {
        'id_report': 0x79,
        'id_uds': 0x701,
        'uds_shift': 0x08,
        'id_command': 0x71,
        'vin_id': 0x811,
        'vin':'NLXXX6666CW006666',
        'start_uniq_key':'aXdloDoospOidd78%',
        'uds_key':'secret_uds_auth',
        'commands': {
                'rpm_up':'01',
                'rpm_down':'02',
                'init': '',
                'stop': '00'
            }

        'reports_delay': 0.6

    }

    """


    _active = True
    def do_init(self, params):
        self._status2 = params
        self._vin = self._status2.get("vin","NLXXX6666CW006666")
        self._auth = self._status2.get("start_uniq_key","tGh&ujKnf5$rFgvc1")
        self._uds_auth = self._status2.get("uds_key","secret_uds_auth1")
        self._seed = None
        self._uds_auth_done = False
        self._status2.update({'rpm':0,'status':0})
        self.rpm_up = 0
        self.rpm_down = 0
        self.default = 500
        self.current = 0
        self.frames = []
        self.init_sess = None
        self.init_sess2 = None
        self._last_sent = time.clock()
        self.vin_gen = [time.clock(), time.clock(),0.7, 2.9]

        left = len(self._vin)
        count = int(left / 7) + 1
        if (left % 7) > 0:
            count += 1
        curr = 0
        self.vin = []
        self.count_part = 0
        while left > 0:
            if curr == 0:
                self.vin.append([0,0,0,0,count,0,0 , left])
                curr += 1
            else:
                part = [ord(byt) for byt in (self._vin[(curr-1)*7:(curr-1)*7+7])]
                self.vin.append([curr] + list(part + list(bytes(7-len(part)))))
                left += -7
                curr += 1

    def generate_rpm(self):
        if self._status2['status'] == 1:
            self.current +=  self.rpm_up - self.rpm_down
            self._status2['rpm'] = self.current + random.randrange(-20, 20)
            if self._status2['rpm'] < 150:
                self._status2['status'] = 2 # dead
            elif self._status2['rpm'] > 4500:
                self._status2['status'] = 2 # also dead

        elif self._status2['status'] == 3:
            self._status2['rpm'] = 0

        elif self._status2['status'] == 2:
            self._status2['rpm'] = 0

        self.rpm_up = 0
        self.rpm_down = 0


        if self._status2['status'] in  [2,3,1]:
            if (time.clock() - self._last_sent) >= self._status2.get('reports_delay',0.5):
                self.frames.append(CANMessage(
                        self._status2.get('id_report',0xffff),
                        3,
                        self._status2['status'].to_bytes(1, byteorder = 'big') + self._status2['rpm'].to_bytes(2, byteorder = 'big'), False,
                        CANMessage.DataFrame
                    ))
                self._last_sent = time.clock()

    def generate_vin(self):
        curr_t = time.clock()
        if self.vin_gen[0] == 0 or curr_t - self.vin_gen[0] > self.vin_gen[2]:
            if self.vin_gen[1] == 0 or curr_t - self.vin_gen[1] > self.vin_gen[3]:
                self.frames.append(CANMessage.init_data(self._status2.get('vin_id',1), len(self.vin[self.count_part]), self.vin[self.count_part]))
                self.count_part+=1
                self.vin_gen[1] = curr_t
                if self.count_part == len(self.vin):
                    self.vin_gen[0] = curr_t
                    self.count_part = 0

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if self._status2['status'] > 0:
            self.generate_rpm()
        self.generate_vin()
        if args['action'] == 'read' and can_msg.CANData: # READ
            if self._status2['id_command'] == can_msg.CANFrame.frame_id:
                for cmd, value in self._status2['commands'].items():
                    len_cmd = int(len(str(value))/2)

                    if self._status2['status'] != 0 and cmd == "rpm_up":
                        len_cmd2 = len_cmd + 1
                        if can_msg.CANFrame.frame_length == len_cmd2 and can_msg.CANFrame.frame_raw_data[0:len_cmd] == bytes.fromhex(value)[0:len_cmd] and self._status2['status'] == 1:
                            self.rpm_up += ord(can_msg.CANFrame.frame_raw_data[len_cmd:len_cmd2])
                    elif self._status2['status'] != 0 and cmd == "rpm_down":
                        len_cmd2 = len_cmd + 1
                        if can_msg.CANFrame.frame_length == len_cmd2 and can_msg.CANFrame.frame_raw_data[0:len_cmd] == bytes.fromhex(value)[0:len_cmd] and self._status2['status'] == 1:
                            self.rpm_down += ord(can_msg.CANFrame.frame_raw_data[len_cmd:len_cmd2])
                    elif self._status2['status'] != 0 and cmd == "stop":
                        if can_msg.CANFrame.frame_length == len_cmd and can_msg.CANFrame.frame_raw_data[0:len_cmd] == bytes.fromhex(value)[0:len_cmd]:
                            self._status2['status'] = 3
                            self.current = 0
                    elif cmd == "init":
                        if not self.init_sess:
                            self.init_sess = ISOTPMessage(can_msg.CANFrame.frame_id)

                        ret = self.init_sess.add_can(can_msg.CANFrame)
                        if ret < 0:
                            self.init_sess = None
                        elif ret == 1:
                            if self.init_sess.message_length != 17:
                                self.init_sess = None
                            else:
                                key = self.init_sess.message_data
                                i = 0
                                vin_x = ""
                                for byte_k in key:
                                    vin_x += chr(byte_k ^ ord(self._auth[i]))  # XOR with KEY (to get VIN)
                                    i+=1
                                if vin_x != self._vin:          # auth failed, send error back
                                    self.frames.append(
                                        CANMessage(
                                            self._status2.get('id_report',0xffff),
                                            2,
                                            b'\xff\xff', False,
                                            CANMessage.DataFrame
                                        )
                                    )
                                else:                          # Auth complite
                                    self._status2['status'] = 1
                                    self.frames.append(
                                        CANMessage(
                                            self._status2.get('id_report',0xffff),
                                            2,
                                            b'\xff\x01', False,
                                            CANMessage.DataFrame
                                        )
                                    )
                                    if self.current < 150:
                                        self.current = self.default
                                self.init_sess = None


            elif self._status2['id_uds'] == can_msg.CANFrame.frame_id:
                    if not self.init_sess2:
                        self.init_sess2 = ISOTPMessage(can_msg.CANFrame.frame_id)

                    ret = self.init_sess2.add_can(can_msg.CANFrame)

                    if ret < 0:
                        self.init_sess2 = None
                    elif ret == 1:
                        uds_msg = UDSMessage(self._status2.get('uds_shift',8))
                        uds_msg.add_raw_request(self.init_sess2)
                        if can_msg.CANFrame.frame_id in uds_msg.sessions:
                            if 0x27 in uds_msg.sessions[can_msg.CANFrame.frame_id]: # Check service
                                if 1 in uds_msg.sessions[can_msg.CANFrame.frame_id][0x27]:  # Check sub: SEED request
                                    self._seed = [random.randrange(1, 100),random.randrange(1, 100),random.randrange(1, 100),random.randrange(1, 100)]
                                    # Generate UDS reponse
                                    self.frames.extend(uds_msg.add_request(
                                        self._status2['id_uds'] + self._status2['uds_shift'], # ID
                                        0x27 + 0x40,                                        # Service
                                        0x01,                                               # Sub function
                                        self._seed))                                        # data

                                elif 2 in uds_msg.sessions[can_msg.CANFrame.frame_id][0x27]: # Check sub: KEY enter
                                    if self._seed != None:
                                        key_x = ""
                                        key = uds_msg.sessions[can_msg.CANFrame.frame_id][0x27][2]['data'] # Read key
                                        i = 0
                                        for byte_k in key:
                                            key_x += chr(byte_k ^ self._seed[i % 4])
                                            i += 1
                                        if key_x == self._uds_auth:
                                            self._uds_auth_done = True
                                            self.frames.extend(uds_msg.add_request(
                                                self._status2['id_uds'] + self._status2['uds_shift'], # ID
                                                0x27 + 0x40,                                        # Service
                                                0x02,                                               # Sub function
                                                [0xFF]))                                        # data
                                        else:
                                            self._uds_auth_done = False
                                            self.frames.extend(uds_msg.add_request(
                                                self._status2['id_uds'] + self._status2['uds_shift'], # ID
                                                0x27 + 0x40,                                        # Service
                                                0x02,                                               # Sub function
                                                [0x00]))                                        # data
                                    self._seed = None
                            elif 0x2e in uds_msg.sessions[can_msg.CANFrame.frame_id] and 0x55 in uds_msg.sessions[can_msg.CANFrame.frame_id][0x2e] and uds_msg.sessions[can_msg.CANFrame.frame_id][0x2e][0x55]['data'][0] == 0x55:
                                if  self._uds_auth_done:
                                    new_key = ''.join(chr(x) for x in uds_msg.sessions[can_msg.CANFrame.frame_id][0x2e][0x55]['data'][1:])
                                    if len(new_key) == 17:
                                        self._uds_auth_done = False
                                        self._auth = new_key
                                        self.frames.extend(uds_msg.add_request(
                                                    self._status2['id_uds'] + self._status2['uds_shift'], # ID
                                                    0x2e + 0x40,                                        # Service
                                                    0x55,                                               # Sub function
                                                    [0x55]))                                        # data
                                    else:
                                        self._uds_auth_done = False
                                        self.frames.extend(uds_msg.add_request(
                                                    self._status2['id_uds'] + self._status2['uds_shift'], # ID
                                                    0x2e + 0x40,                                        # Service
                                                    0x00,                                               # Sub function
                                                    [0x00]))
                                else:
                                    self._uds_auth_done = False
                                    self.frames.extend(uds_msg.add_request(
                                                self._status2['id_uds'] + self._status2['uds_shift'], # ID
                                                0x2e + 0x40,                                        # Service
                                                0x00,                                               # Sub function
                                                [0x00]))                                        # data
                        self.init_sess2 = None

        elif args['action'] == 'write' and not can_msg.CANData:
            if len(self.frames) > 0:
                can_msg.CANFrame = self.frames.pop(0)
                can_msg.CANData = True
                can_msg.bus = self._bus
        return can_msg
