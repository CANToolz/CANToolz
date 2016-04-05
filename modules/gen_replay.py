from libs.module import *
from libs.can import *


class gen_replay(CANModule):
    name = "Replay module"
    help = """
    
    This module doing replay of captured packets. 
    
    Init parameters:
        load_from  - load packets from file (optional)
        save_to    - save to file (mod_replay.save by default)

    Module parameters: none

    """

    _fname = None

    CANList = []

    _active = True
    version = 1.0

    _replay = False
    _sniff = False

    def get_status(self):
        return "Current status: " + str(self._active) + "\nSniff mode: " + str(self._sniff) +\
               "\nReplay mode: " + str(self._replay) +"\nFrames in queue: " + str(len(self.CANList))

    def cmd_load(self, name):
        try:
            with open(name.strip(), "r") as ins:
                for line in ins:
                    fid = line[:-1].split(":")[0]
                    length = line[:-1].split(":")[1]
                    data = line[:-1].split(":")[2]
                    self.CANList.append(CANMessage.init_data(int(fid), int(length), [struct.unpack("B", x)[0] for x in
                                                                                     data.decode('hex')[:8]]))
                self.dprint(1, "Loaded " + str(len(self.CANList)) + " frames")
        except:
            self.dprint(2, "can't open files with CAN messages!")
        return "Loaded: " + str(len(self.CANList))

    def do_init(self, params):
        self.CANList = []
        if 'save_to' in params:
            self._fname = params['save_to']
        else:
            self._fname = "mod_replay.save"

        if 'load_from' in params:
            try:
                with open(params['load_from'], "r") as ins:
                    for line in ins:
                        fid = line[:-1].split(":")[0]
                        length = line[:-1].split(":")[1]
                        data = line[:-1].split(":")[2]
                        self.CANList.append(
                            CANMessage.init_data(int(fid), int(length), [struct.unpack("B", x)[0] for x in
                                                                         data.decode('hex')[:8]]))
                self.dprint(1, "Loaded " + str(len(self.CANList)) + " frames")
            except:
                self.dprint(2, "can't open files with CAN messages!")

        self._cmdList['g'] = ["Enable/Disable sniff mode to collect packets", 0, "", self.sniff_mode]
        self._cmdList['p'] = ["Print count of loaded packets", 0, "", self.cnt_print]
        self._cmdList['l'] = ["Load packets from file", 1, " <file> ", self.cmd_load]
        self._cmdList['r'] = ["Replay range from loaded, from number X to number Y", 1, " <X>-<Y> ", self.replay_mode]
        self._cmdList['d'] = ["Save range of loaded packets, from X to Y", 1, " <X>-<Y>, <filename>",self.save_dump]
        self._cmdList['c'] = ["Clean loaded table", 0, "", self.clean_table]


    def clean_table(self):
        self.CANList = []
        return "Replay buffer is clean!"

    def save_dump(self, input_params):
        fname = self._fname
        indexes = input_params.split(',')[0].strip()
        if len(input_params.split(',')) > 1:
            fname = input_params.split(',')[1].strip()

        ret = "Saved to " + fname

        try:
            _num1 = int(indexes.split("-")[0])
            _num2 = int(indexes.split("-")[1])
        except:
            _num1 = 0
            _num2 = len(self.CANList)
        if len(self.CANList) >= _num2 > _num1 >= 0:
            try:
                _file = open(fname, 'w')
                for i in range(_num1, _num2):
                    _file.write(str(self.CANList[i].frame_id) + ":" + str(self.CANList[i].frame_length) + ":" + str(
                        self.CANList[i].frame_raw_data.encode('hex')) + "\n")
                _file.close()
            except Exception as e:
                ret = "Not saved. Error: " + str(e)
        return ret

    def sniff_mode(self):
        self._replay = False
        if self._sniff:
            self._sniff = False
        else:
            self._sniff = True
        return str(self._sniff)

    def replay_mode(self, indexes):
        self._replay = False
        self._sniff = False
        try:
            self._num1 = int(indexes.split("-")[0])
            self._num2 = int(indexes.split("-")[1])
            if self._num2 > self._num1 and self._num1 < len(self.CANList) and self._num2 <= len(
                    self.CANList) and self._num1 >= 0 and self._num2 > 0:
                self._replay = True
        except:
            self._replay = False

        return "Replay mode changed to: " + str(self._replay)

    def cnt_print(self):
        ret = str(len(self.CANList))
        return "Loaded packets: " + ret

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if self._sniff and can_msg.CANData:
            self.CANList.append(can_msg.CANFrame)
        elif self._replay:
            can_msg.CANFrame = self.CANList[self._num1]
            self._num1 += 1
            can_msg.CANData = True
            if self._num1 == self._num2:
                self._replay = False
        return can_msg
