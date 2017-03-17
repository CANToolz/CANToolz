from cantoolz.module import *
from cantoolz.replay import *
import time
import codecs

class gen_replay(CANModule):
    name = "Replay module"
    help = """
    
    This module doing replay of captured packets. 
    
    Init parameters:
        load_from  - load packets from file (optional)
        save_to    - save to file (mod_replay.save by default)

    Module parameters: none
        delay  - delay between frames (0 by default)

    """

    _fname = None

    _active = True
    version = 1.0

    _replay = False
    _sniff = False

    def get_status(self, def_in):
        return "Current status: " + str(self._active) + "\nSniff mode: " + str(self._sniff) +\
               "\nReplay mode: " + str(self._replay) +"\nFrames in memory: " + str(len(self.CANList)) +\
               "\nFrames in queue: " + str(self._num2 - self._num1)

    def cmd_load(self, def_in, name):
        try:
                self.CANList.parse_file(name, self._bus)
                self.dprint(1, "Loaded " + str(len(self.CANList)) + " frames")
        except Exception as e:
            self.dprint(2, "can't open files with CAN messages: " + str(e))
        return "Loaded: " + str(len(self.CANList))

    def do_init(self, params):
        self.CANList = Replay()
        self.last = time.clock()
        self._last = 0
        self._full = 1
        self._num1 = 0
        self._num2 = 0
        if 'save_to' in params:
            self._fname = params['save_to']
        else:
            self._fname = "mod_replay.save"

        if 'load_from' in params:
            self.cmd_load(0, params['load_from'])

        self._cmdList['g'] = Command("Enable/Disable sniff mode to collect packets", 0, "", self.sniff_mode, True)
        self._cmdList['p'] = Command("Print count of loaded packets", 0, "", self.cnt_print, True)
        self._cmdList['l'] = Command("Load packets from file", 1, " <file> ", self.cmd_load, True)
        self._cmdList['r'] = Command("Replay range from loaded, from number X to number Y", 1, " <X>-<Y> ", self.replay_mode, True)
        self._cmdList['d'] = Command("Save range of loaded packets, from X to Y", 1, " <X>-<Y>, <filename>",self.save_dump, True)
        self._cmdList['c'] = Command("Clean loaded table", 0, "", self.clean_table, True)


    def clean_table(self, def_in):
        self.CANList = Replay()
        self._last = 0
        self._full = 1
        self._num1 = 0
        self._num2 = 0
        return "Replay buffer is clean!"

    def save_dump(self, def_in, input_params):
        fname = self._fname
        indexes = input_params.split(',')[0].strip()
        if len(input_params.split(',')) > 1:
            fname = input_params.split(',')[1].strip()

        try:
            _num1 = int(indexes.split("-")[0])
            _num2 = int(indexes.split("-")[1])
        except:
            _num1 = 0
            _num2 = len(self.CANList)
        ret = self.CANList.save_dump(fname, _num1, _num2 - _num1)
        return ret

    def sniff_mode(self, def_in):
        self._replay = False

        if self._sniff:
            self._sniff = False
            self._cmdList['r'].is_enabled = True
            self._cmdList['d'].is_enabled = True
        else:
            self._sniff = True
            self._cmdList['r'].is_enabled = False
            self._cmdList['d'].is_enabled = False
            self.CANList.restart_time()
        return str(self._sniff)

    def replay_mode(self, def_in, indexes = None):
        self._replay = False
        self._sniff = False
        if not indexes:
            indexes = "0-"+str(len(self.CANList))
        try:
            self._num1 = int(indexes.split("-")[0])
            self._num2 = int(indexes.split("-")[1])
            if self._num2 > self._num1 and self._num1 < len(self.CANList) and self._num2 <= len(
                    self.CANList) and self._num1 >= 0 and self._num2 > 0:
                self._replay = True
                self._full = self._num2 - self._num1
                self._last = 0
                self._cmdList['g'].is_enabled =  False
                self.CANList.set_index(self._num1)


        except:
            self._replay = False

        return "Replay mode changed to: " + str(self._replay)

    def cnt_print(self, def_in):
        ret = str(len(self.CANList))
        return "Loaded packets: " + ret

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if self._sniff and can_msg.CANData:
            self.CANList.append(can_msg)
        elif self._replay and not can_msg.CANData:
            d_time = float(args.get('delay', 0))
            ignore = bool(args.get('ignore_time', False))
            try:
                next_msg = self.CANList.next(d_time, ignore)
                if next_msg and next_msg.CANData:
                    can_msg.CANFrame = next_msg.CANFrame
                    self._num1 += 1
                    can_msg.CANData = True
                    self._last += 1
                can_msg.bus = self._bus
                self._status = self._last/(self._full/100.0)
            except Exception as e:
                self._replay = False
                self._cmdList['g'].is_enabled = True
                self.CANList.reset()
            if self._num1 == self._num2:
                self._replay = False
                self._cmdList['g'].is_enabled = True
                self.CANList.reset()
        return can_msg
