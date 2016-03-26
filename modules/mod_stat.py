from libs.module import *
from libs.uds import *
import collections


class mod_stat(CANModule):
    name = "Service discovery and statistic"

    help = """
    
    This module doing statistic for found CAN messages, putting into STDOUT or file (text/csv).
    Good to see anomalies, behaviour and discovery new IDs
    
    Init parameters: NONE
       
    """

    _bodyList = None
    _logFile = False
    ISOList = None
    UDSList = None
    id = 3
    _active = True
    version = 1.0
    _alert = False

    def do_open_files(self):
        if self._logFile:
            try:
                self._file = open(self._fname, 'w')
            except:
                self.dprint(2, "can't open log")

                #    def doStop(self):
                #        if self._logFile:
                #            try:
                #                self._file.close()
                #            except:
                #                self.dprint(2,"can't open log")

    def do_init(self, params):

        self._bodyList = collections.OrderedDict()
        self.ISOList = collections.OrderedDict()

        self.shift = params.get('shift', 8)
        self.UDSList = UDSMessage(self.shift)

        self._cmdList['p'] = ["Print current table", 0, "", self.do_print]
        self._cmdList['a'] = ["Analyses of captured traffic", 0, "", self.do_anal]
        self._cmdList['c'] = ["Clean table, remove alerts", 0, "", self.do_clean]
        self._cmdList['m'] = ["Enable alert mode and insert mark into the table", 1, "<ID>", self.add_alert]
        self._cmdList['r'] = ["Dump ALL in replay format", 1, " <filename>", self.do_dump_replay]
        self._cmdList['d'] = ["Dump ALL in CSV format", 1, " <filename>", self.do_dump_csv]


    def do_anal(self):
        ret_str = "ISO TP Messages:\n"
        for fid, lst in self._bodyList.iteritems():
            message_iso = ISOTPMessage(fid)
            for (lenX, msg, bus, mod), cnt in lst.iteritems():
                if lenX < 2:
                    continue
                ret = message_iso.add_can(CANMessage.init_data(fid, len(msg), [struct.unpack("B", x)[0] for x in msg])) # TODO NEED RET?
                if ret < 0:
                     message_iso = ISOTPMessage(fid)
                if message_iso.message_finished and message_iso.message_length > 0 and ret == 1:
                    if fid not in self.ISOList:
                        self.ISOList[fid] = []
                    self.ISOList[fid].append((bus, message_iso.message_length, message_iso.message_data))
                    ret_str += "\tID " + str(fid) + " and length " + str(message_iso.message_length) + "\n"
                    ret_str += "\t\tData: " + ''.join(struct.pack("!B", b).encode('hex') for b in message_iso.message_data)
                    ret_str += "\n\t\tASCII: " + ''.join(struct.pack("!B", b) for b in message_iso.message_data)+"\n\n"
                    # Check for UDS
                    self.UDSList.handle_message(message_iso)
                    message_iso = ISOTPMessage(fid)

        ret_str += "\n\nUDS found:\n"
        for fid, services in self.UDSList.sessions.iteritems():
            for service, body in services.iteritems():
                text = " (N/A) "
                if service in UDSMessage.services_base:
                    for sub in UDSMessage.services_base[service]:
                        if sub.keys()[0] == body['sub'] or None:
                            text = " (" + sub.values()[0] + ") "
                    if text == " (N/A) ":
                        text = " (" + UDSMessage.services_base[service][0].values()[0] + ") "
                if body['status'] == 1:
                    data = ''.join(struct.pack("!B", b) for b in body['response']['data'])
                    ret_str += "\n\tID: " + str(fid) + " Service: " + str(hex(service)) + " Sub: " + (str(
                        hex(body['sub'])) if body['sub'] else "None") + text + "\n\t\tResponse: " + data.encode('hex') + " ASCII: " + data
                elif body['status'] == 2:
                    ret_str += "\n\tID: " + str(fid) + " Service: " + str(hex(service)) + " Sub: " + (str(
                        hex(body['sub'])) if body['sub'] else "None") + text + "\n\t\tError: " + body['response']['error']

        return ret_str

    def do_dump_replay(self, name):
        _name = None
        try:
            _name = open(name.strip(), 'w')

            for fid, lst in self._bodyList.iteritems():
                for (lenX, msg, bus, mod), cnt in lst.iteritems():
                    _name.write(str(fid) + ":" + str(lenX) + ":" + msg.encode('hex') + "\n")
            _name.close()
        except:
            self.dprint(2, "can't open log")

    def do_dump_csv(self, name):
        _name = None
        try:
            _name = open(name.strip(), 'w')
            _name.write("BUS,ID,LENGTH,MESSAGE,COUNT\n")
            for fid, lst in self._bodyList.iteritems():
                for (len, msg, bus, mod), cnt in lst.iteritems():
                    _name.write(str(bus) + "," + str(fid) + "," + str(len) + "," + msg.encode('hex') +
                                     ',' + str(cnt) + "\n")
        except:
            self.dprint(2, "can't open log")
        return ""

    def do_print(self):
        table = "\n"
        table += "BUS\tID\tLENGTH\t\tMESSAGE\t\t\tCOUNT"
        table += "\n"
        for fid, lst in self._bodyList.iteritems():
            for (lenX, msg, bus, mod), cnt in lst.iteritems():
                if mod:
                    modx = "\t"
                else:
                    modx = "\t\t"
                sp = " " * (16 - len(msg) * 2)
                table += str(bus) + "\t" + str(fid) + "\t" + str(lenX) + modx + msg.encode('hex') + sp + '\t' + str(
                    cnt) + "\n"
        table += ""
        return table

    def add_alert(self, x):
        self._bodyList[int(x)] = collections.OrderedDict()
        self._bodyList[int(x)][(0, "MARK", 0, False)] = 1
        self._alert = True
        return ""


    def do_clean(self):
        self._bodyList = collections.OrderedDict()
        self._alert = False
        self.ISOList = collections.OrderedDict()
        self.UDSList = UDSMessage(self.shift)
        return ""

        # Effect (could be fuzz operation, sniff, filter or whatever)

    def do_effect(self, can_msg, args):
        if can_msg.CANData:
            if can_msg.CANFrame.frame_id not in self._bodyList:
                self._bodyList[can_msg.CANFrame.frame_id] = collections.OrderedDict()
                self._bodyList[can_msg.CANFrame.frame_id][(
                    can_msg.CANFrame.frame_length,
                    can_msg.CANFrame.frame_raw_data,
                    can_msg.bus,
                    can_msg.CANFrame.frame_ext)
                ] = 1
                if self._alert:
                    self.dprint(1, "New ID found: " + str(can_msg.CANFrame.frame_id) +
                                " (BUS: " + str(can_msg.bus) + ")")
            else:
                if (can_msg.CANFrame.frame_length,
                    can_msg.CANFrame.frame_raw_data,
                    can_msg.bus,
                    can_msg.CANFrame.frame_ext) not in self._bodyList[can_msg.CANFrame.frame_id]:
                    self._bodyList[can_msg.CANFrame.frame_id][(
                        can_msg.CANFrame.frame_length,
                        can_msg.CANFrame.frame_raw_data,
                        can_msg.bus,
                        can_msg.CANFrame.frame_ext)
                    ] = 1
                else:
                    self._bodyList[can_msg.CANFrame.frame_id][(
                        can_msg.CANFrame.frame_length,
                        can_msg.CANFrame.frame_raw_data,
                        can_msg.bus,
                        can_msg.CANFrame.frame_ext)
                    ] += 1

        return can_msg
