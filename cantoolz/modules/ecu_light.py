from cantoolz.module import *
from cantoolz.can import *
import time

class ecu_light(CANModule):
    name = "CAN ECU for the car lights"
    help = """

    This module emulating car's lights.

    Init params (example):

    {
            'id_report': 0x111,
            'id_command': 0x101,
            'commands': {
                'off':'00',
                'on':'01',
                'distance': '02',
            },

            'reports': {
                'LIGHTS ON': 'ff0101',
                'DISTANCE LIGHTS ON': 'ff0202',
                'Lights OFF': '000000',
            },
            'reports_delay': 1.5
    }

    """


    _active = True
    def do_init(self, params):
        self._params = params
        self._params['status'] = 'Lights OFF'
        self._frames = []
        self._last_sent = time.clock()

    def do_start(self, params):
        self._params['status'] = 'Lights OFF'

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if args['action']=='read' and can_msg.CANData: # READ
            if self._params['id_command'] == can_msg.CANFrame.frame_id:
                for cmd, value in self._params['commands'].items():
                    len_cmd = int(len(value)/2)
                    if can_msg.CANFrame.frame_length == len_cmd and can_msg.CANFrame.frame_raw_data[0:len_cmd] == bytes.fromhex(value):
                            if cmd == 'off':
                                self._params['status'] = 'Lights OFF'
                                self._last_sent -=  self._params.get('reports_delay',1.0)
                            if cmd == 'on':
                                self._params['status'] = 'LIGHTS ON'
                                self._last_sent -=  self._params.get('reports_delay',1.0)
                            if cmd == 'distance':
                                self._params['status'] = 'DISTANCE LIGHTS ON'
                            self._last_sent -=  self._params.get('reports_delay',1.0)



        elif  args['action']=='write' and not can_msg.CANData and self._params['status'] != 'Turned off':               # Write
            if (time.clock() - self._last_sent) >= self._params.get('reports_delay',1.0):
                can_msg.CANFrame = CANMessage(
                    self._params.get('id_report',0xffff),
                    len(self._params.get('reports',{}).get(self._params['status'],''))/2,
                    bytes.fromhex(self._params.get('reports',{}).get(self._params['status'],'ffffff')), False,
                    CANMessage.DataFrame
                )
                can_msg.CANData = True
                can_msg.bus = self._bus
                self._last_sent = time.clock()


        return can_msg
