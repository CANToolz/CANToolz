from cantoolz.module import *
from cantoolz.correl import *


class mod_stat_beta(CANModule):
    name = "Service discovery and statistic"

    help = """ """
    
    def do_init(self, params):
        self.all_frames = []
        self._cmdList['s'] = ["Show all fields", 0, "", self.show_fields, True]
        self.subnet = Subnet(lambda stream: Separator(SeparatedMessage.builder))

    def show_fields(self, zd):
        ret_str = ""
        
        for key, value in self.subnet._devices.items():
            ret_str += "ECU: " + str(key) + ", INDEXES: " + str(value._indexes()) + "\n"
            
        return ret_str

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if can_msg.CANData:
            print("X: "+str(can_msg.CANFrame))
            for _ in self.subnet.process(can_msg.CANFrame):
                pass
            
        return can_msg
