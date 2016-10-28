import time
from cantoolz.module import *
from cantoolz.can import *
import copy

class Replay:
    def __init__(self):
        self._stream = []
        self._last = time.clock()
        self._curr = 0
        self._pre_last = 0
        self._shift = 0
        self._size = 0
        self.add_timestamp()

    def reset(self):
        self._last = time.clock()
        self._curr = 0
        self._pre_last = 0

    @property
    def stream(self):
        return copy.deepcopy(self._stream)

    def passed_time(self):
        return time.clock() + self._shift - self._last

    def restart_time(self, shift = 0.0):
        self._last = time.clock() - shift


    def append_time(self, times, can_msg):
        if can_msg.CANData:
            self._stream.append([times, copy.deepcopy(can_msg)])
            self._size += 1

    def append(self, can_msg):
        if can_msg.CANData:
            self._stream.append([self.passed_time(), copy.deepcopy(can_msg)])
            self._size += 1

        elif can_msg.debugData:
            self._stream.append([0.0, copy.deepcopy(can_msg)])

    def set_index(self, i=0):
        if i < len(self):
            self._curr = 0
            curr_can = 0
            for x in self._stream:
                if i == curr_can and x[1].CANData:
                    break
                elif x[1].CANData:
                    curr_can += 1
                self._curr += 1

    def get_message(self, cnt):
        curr_can = 0

        for x in self._stream:
            if cnt == curr_can and x[1].CANData:
                return (x[0], x[1].CANFrame)
            elif x[1].CANData:
                curr_can += 1

        return (None, None)


    def add_timestamp(self, def_time = None):
        msg = CANSploitMessage()
        if not def_time:
            msg.debugText = str(time.time())
        else:
            msg.debugText = str(def_time)
        msg.CANFrame = None
        msg.CANData = False
        msg.debugData = True
        msg.bus = "TIMESTAMP"
        self._pre_last = 0
        self.restart_time()
        self._stream.append( [0.0, msg] )

    def __iter__(self):
        return iter(self._stream)

    def next(self, offset = 0, notime = True):
        if self._curr < len(self._stream):
            if notime:
                if self._stream[self._curr][1].CANData:
                    ret = self._stream[self._curr][1]
                    self._curr += 1
                    return copy.deepcopy(ret)
                else:
                    self._curr += 1
                    return None
            else:
                if self._stream[self._curr][1].debugData:
                    self.restart_time()
                    self._pre_last = 0
                    self._curr += 1
                    return None
                if self._stream[self._curr][0] < self._pre_last:
                    self._pre_last = 0

                if self._pre_last != 0.0 and self._stream[self._curr][0] >= 0 and self.passed_time() > (self._stream[self._curr][0]):
                    time.sleep(offset)
                    self._pre_last = self._stream[self._curr][0]
                    ret = self._stream[self._curr][1]
                    self._curr += 1
                    return copy.deepcopy(ret)
                elif self._pre_last == 0.0:
                    time.sleep(offset)
                    self._pre_last = self._stream[self._curr][0]
                    ret = self._stream[self._curr][1]
                    self.restart_time(self._stream[self._curr][0])
                    self._curr += 1
                    return copy.deepcopy(ret)
                elif (self._stream[self._curr][0] < 0):
                    time.sleep(offset)
                    self.restart_time()
                    self._pre_last = 0.0
                    ret = self._stream[self._curr][1]
                    self._curr += 1
                    return copy.deepcopy(ret)
                else:
                    return None
        else:
            self._curr = 0
            return Exception('No more messages!')

    def __add__(self, other):
        newRep = Replay()
        newRep._size = len(self) + len(other)
        new = copy.deepcopy(other)
        if (len(self)) > 0:
            last_time = self.get_message(len(self)-1)[0]
        else:
            last_time = 0
        for each in new._stream:
            each[0] += last_time
        newRep._stream = self._stream + new._stream

        return newRep

    def __len__(self):
        return self._size

    def parse_file(self, name, _bus):
        try:
            with open(name.strip(), "r") as ins:
                # "[TIME_STAMP]0x111:4:11223344"
                for line in ins:
                    if len(line[:].split(":")) >= 3:
                        fid = line[:].split(":")[0].strip()

                        if fid[0] == "[" and fid.find(']') > 0:
                            time_stamp = float(fid[1:fid.find(']')])
                            fid = fid.split(']')[1].strip()
                        elif fid[0] == "<" and fid.find('>') > 0:
                            time_stamp = float(fid[1:fid.find('>')])
                            self.add_timestamp(time_stamp)
                            continue
                        elif len(line[:-1].split(":")) >= 3:
                            time_stamp = -1.0
                        else:
                            time_stamp = -1.0

                        if fid.find('0x') == 0:
                            num_fid = int(fid, 16)
                        else:
                            num_fid = int(fid)

                        length = line[:].split(":")[1]
                        data = line[:].split(":")[2]
                        if data[-1:] == "\n":
                            data = data[:-1]
                        if data[-1:] == "\r":
                            data = data[:-1]
                        msg = CANSploitMessage()
                        msg.CANFrame = CANMessage.init_data(num_fid, int(length), bytes.fromhex(data)[:8])
                        msg.CANData = True
                        msg.bus = _bus
                        self._stream.append([time_stamp, msg])
                        self._size += 1


        except Exception as e:
            print(str(e))
            return "Can't open files with CAN messages: " + str(e)
        return "Loaded from file: " + str(len(self)) + " messages"

    def remove_by_id(self, idf):
        i = 0
        for times, msg in self._stream:
            if msg.CANData and msg.CANFrame.frame_id == idf:
                self._stream[i][1].CANData = False
                self._size -= 1
            i += 1
    def search_messages_by_id(self, idf):
        i = 0
        ret = []
        for times, msg in self._stream:
            if msg.CANData and msg.CANFrame.frame_id == idf:
                ret.append(msg.CANFrame.frame_raw_data)
            i += 1
        return ret

    def save_dump(self, fname, offset = 0, amount = -1):

        if amount <= 0 :
            amount = len(self)

        ret = "Saved to " + fname

        try:
            _num1 = offset
            _num2 = offset + amount
        except:
            _num1 = 0
            _num2 = len(self)

        if len(self) >= _num2 > _num1 >= 0:
            try:
                _file = open(fname, 'w')
                #for i in range(_num1, _num2):
                curr = 0
                for times, msg in self._stream:
                    if curr < _num1:
                        continue
                    elif curr >= _num2:
                        break

                    if not msg.debugData and msg.CANData:
                        _file.write((("[" + str(times) + "]") if times >= 0.0 else "") + msg.CANFrame.get_text() + "\n")
                        curr += 1
                    elif msg.debugData:
                        _file.write("<" + str(msg.debugText) + ">\n")

                _file.close()
            except Exception as e:
                ret = "Not saved. Error: " + str(e)
        return ret
