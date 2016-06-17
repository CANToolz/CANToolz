import time
from cantoolz.module import *
from cantoolz.can import *

class Replay:
    def __init__(self):
        self._stream = []
        self._last = time.clock()
        self._curr = 0
        self._pre_last = 0
        self._shift = 0

    def reset(self):
        self._last = time.clock()
        self._curr = 0
        self._pre_last = 0
        self._shift = 0

    @property
    def stream(self):
        return self._stream

    def passed_time(self):
        return time.clock() + self._shift - self._last

    def restart_time(self, shift=0.0):
        self._last = time.clock()
        self._pre_last = shift
        self._shift =  shift

    def append(self, can_msg):
        self._stream.append((self.passed_time(), can_msg))

    def start(self, i = 0):
        if i < len(self):
            self._curr = i
            self._pre_last = self._stream[self._curr][0]
            self._last = time.clock()
            self._shift = self._stream[self._curr][0]
        else:
            return Exception('Cant start, cos empty!')

    def __iter__(self):
        return iter(self._stream)

    def next(self, offset = 0, notime = True):
        if self._curr < len(self):
            if not notime and self._stream[self._curr][0] < self._pre_last:
                self.restart_time(self._stream[self._curr][0])
            if not notime and (self._stream[self._curr][0] >= 0 and self.passed_time() > (self._stream[self._curr][0] + offset)):
                self._pre_last = self._stream[self._curr][0]
                ret = self._stream[self._curr][1]
                self._curr += 1
                return ret
            elif (self._stream[self._curr][0] < 0) or notime:
                time.sleep(offset)
                self._pre_last = self._stream[self._curr][0]
                ret = self._stream[self._curr][1]
                self._curr += 1
                return ret
            else:
                return None
        else:
            return Exception('No more messages!')

    def __add__(self, other):
        return self._stream + other.stream

    def __len__(self):
        return len(self._stream)

    def parse_file(self, name, _bus):
        try:
            with open(name.strip(), "r") as ins:
                # "[TIME_STAMP]0x111:4:11223344"
                for line in ins:
                    fid = line[:-1].split(":")[0].strip()
                    if fid[0] == "[" and fid.find(']') > 0:
                        time_stamp = float(fid[1:fid.find(']')])
                        fid = fid.split(']')[1].strip()
                    else:
                        time_stamp = -1.0
                    if fid.find('0x') == 0:
                        num_fid = int(fid, 16)
                    else:
                        num_fid = int(fid)
                    length = line[:-1].split(":")[1]
                    data = line[:-1].split(":")[2]
                    msg = CANSploitMessage()
                    msg.CANFrame = CANMessage.init_data(num_fid, int(length), bytes.fromhex(data)[:8])
                    msg.CANData = True
                    msg.bus = _bus
                    self._stream.append((time_stamp, msg))
        except Exception as e:
            return "Can't open files with CAN messages: " + str(e)
        return "Loaded from file: " + str(len(self)) + " messages"

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
                for i in range(_num1, _num2):
                    _file.write((("[" + str(self._stream[i][0]) + "]") if self._stream[i][0] >= 0.0 else "") + (hex(self._stream[i][1].CANFrame.frame_id) + ":" + str(self._stream[i][1].CANFrame.frame_length) + ":" +
                        CANModule.get_hex(self._stream[i][1].CANFrame.frame_raw_data) + "\n"))
                _file.close()
            except Exception as e:
                ret = "Not saved. Error: " + str(e)
        return ret

    def return_dump(self, offset = 0, amount = -1):
        if amount <= 0 :
            amount = len(self)

        ret = []

        try:
            _num1 = offset
            _num2 = offset + amount
        except:
            _num1 = 0
            _num2 = len(self)

        if len(self) >= _num2 > _num1 >= 0:
            try:
                for i in range(_num1, _num2):
                    ret.append([(str(self._stream[i][0]) if self._stream[i][0] >= 0.0 else ""), hex(self._stream[i][1].CANFrame.frame_id), str(self._stream[i][1].CANFrame.frame_length),
                        CANModule.get_hex(self._stream[i][1].CANFrame.frame_raw_data)])

            except Exception as e:
                return ret
        return ret
