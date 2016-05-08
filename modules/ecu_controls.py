from libs.module import *
from libs.can import *
import re

class ecu_controls(CANModule):
    name = "Controls for ECU"
    help = """
    
    This module read statues and send commands.
    
    Init parameters:
    AS Init parameters you can configure commands and statuses parser (regex)

     {'commands':[
        {'Unlock':'0x122:2:fff0'},
        {'Lock'  :'0x122:2:ffff'},
        {'Open Trunk':'290:2:ffa0'}
     ],

     'statuses':[

     {'Door  - Rear passenger':{
        'Open':'0x133#ff.*',
        'Closed':'0x133#00.*'
     }},

     {'Door  - Front driver':{
        'Open':'0x133#..FF.*',
        'Closed':'0x133#..00.*'
     }}

     ]}
    

    
    """


    _active = True
    def do_init(self, params):
        self._statuses = params.get('statuses',[])
        self._commands = params.get('commands',[])
        self._frames = []

        cmd_list = [chr(i) for i in ( list(range(0x41,0x41+26)) + list(range(0x61,0x61+26))) if i not in self._cmdList.keys()]
        index = 0

        for command in self._commands:
            self._cmdList[cmd_list.pop()] = ["Action: " + list(command.keys())[0],0,'', self.send_command, True, index]
            index += 1
        index = 0
        for status in self._statuses:
            self._cmdList[cmd_list.pop()] = ["Status: " + list(status.keys())[0],0,'', self.get_statuses, True, index]
            index += 1
            fid_list = []
            for name, data in status.items():
                for act, frame in data.items():
                    fid =  frame.split("#")[0].strip()
                    if fid[0:2] == '0x':
                        fid = int(fid,16)
                    else:
                        fid = int(fid)
                    if fid not in fid_list:
                        fid_list.append(fid)
            status['id_list_can_toolz_system'] = fid_list

    def get_statuses(self, index):
        status = self._statuses[index].get('current_status', 'Unknown')
        name = list([x for x in list(self._statuses[index].keys()) if not x == "id_list_can_toolz_system"])[0]
        return name + " is " + status

    def send_command(self, index):
        cmd = self._commands[index]
        name = list(cmd.keys())[0].strip()
        (fid, length, data_hex) = list(cmd.values())[0].split(":")
        fid = fid.strip()
        length = int(length)
        data_hex = data_hex.strip()

        if fid[0:2] == '0x':
            fid = int(fid,16)
        else:
            fid = int(fid)

        data_hex = bytes.fromhex(data_hex)[:8]

        self._frames.append(CANMessage.init_data(fid, length, data_hex))
        return name + " has been added to queue!"

    def read_statuses(self,can_msg):
        for status in self._statuses:
           if can_msg.CANFrame.frame_id in status.get('id_list_can_toolz_system', []):
               data_hex = can_msg.CANFrame.frame_raw_data.hex()
               for stat, options in list(status.items()):
                   if stat not in ['id_list_can_toolz_system', 'current_status']:
                        for value, reg in list(options.items()):
                            reg = reg.split('#')[1].strip()
                            if re.match(reg, data_hex, re.IGNORECASE):
                                status['current_status'] = value


    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if can_msg.CANData:
            self.read_statuses(can_msg)
        else:
            if len(self._frames) > 0:
                can_msg.CANFrame = self._frames.pop()
                can_msg.CANData = True
                can_msg.bus = self._bus
        return can_msg
