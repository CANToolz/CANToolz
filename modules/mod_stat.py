from libs.module import *
from libs.uds import *
from libs.frag import *
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
        self.all_frames = []
        self.meta_data = {}
        self._bodyList = collections.OrderedDict()


        self.shift = params.get('uds_shift', 8)

        if 'meta_file' in params:
            self.dprint(1, self.do_load_meta(params['meta']))

        self._cmdList['p'] = ["Print current table", 0, "", self.do_print]
        self._cmdList['a'] = ["Analyses of captured traffic", 1, "<UDS|ISO|FRAG|ALL(defaulr)>", self.do_anal]
        self._cmdList['c'] = ["Clean table, remove alerts", 0, "", self.do_clean]
        self._cmdList['i'] = ["Meta-data: add description for ID", 1, "<ID>, <description>", self.do_add_meta_descr]
        self._cmdList['x'] = ["Meta-data: add index-byte for ID", 1, "<ID>, <index>-<range>-<start_value>", self.do_add_meta_index]
        self._cmdList['l'] = ["Load meta-data", 1, "<filename>", self.do_load_meta]
        self._cmdList['z'] = ["Save meta-data", 1, "<filename>", self.do_save_meta]
        self._cmdList['r'] = ["Dump ALL in replay format", 1, " <filename>", self.do_dump_replay]
        self._cmdList['d'] = ["Dump STAT in CSV format", 1, " <filename>", self.do_dump_csv]

    def do_add_meta_descr(self, input_params):
        try:
            fid, descr = input_params.split(',')
            if int(fid) not in self.meta_data:
                self.meta_data[int(fid)] = {}
            self.meta_data[int(fid)]['id_descr'] = descr.strip()
            return "Description added"
        except Exception as e:
            return "Description META error: " + str(e)

    def do_add_meta_index(self, input_params):
        try:
            fid, idx = input_params.split(',')
            fid = int(fid)
            if idx.find("-") > 0 and int(idx.split('-')[0]) >= 0 and int(idx.split('-')[1]) >= 0 and int(idx.split('-')[2]) >= 0:
                if int(fid) not in self.meta_data:
                    self.meta_data[fid] = {}
                self.meta_data[fid]['id_index'] = idx.strip()
                return "Index added"
            else:
                return "Wrong INDEX format (Should be: <from_index> -  <to_index> - <start_value_of_index>)"
        except Exception as e:
            return "Description META error: " + str(e)

    def do_load_meta(self, filename):
        try:
            with open(filename.strip(), "r") as ins:
                for line in ins:
                    frame_id = int(line[:-1].split(":")[0].strip())
                    type_data = line[:-1].split(":")[1].strip()
                    data = line[:-1].split(":")[2].strip()

                    if frame_id not in self.meta_data:
                        self.meta_data[frame_id] = {}

                    self.meta_data[frame_id][type_data] = data
        except Exception as e:
            return "Can't load META: " + str(e)
        return "Loaded META from " + filename

    def do_save_meta(self, filename):
        try:
            _file = open(filename.strip(), 'w')
            for (key, value) in self.meta_data.iteritems():
                for (tp, data) in value.iteritems():
                    _file.write(str(key) + ":" + tp + ":" + data + "\n")
            _file.close()
        except Exception as e:
            return "Can't save META: " + str(e)
        return "Saved META to " + filename

    # Detect ASCII data
    @staticmethod
    def ret_ascii(text_array):
        return_str = ""
        for byte in text_array:
            if 31 < ord(byte) < 127:
                return_str += byte
            else:
                return_str += '.'
        return return_str

    # Detect ASCII data
    @staticmethod
    def is_ascii(text_array):
        bool_ascii = False
        ascii_cnt = 0
        pre_byte = False

        for byte in text_array:
            if 31 < byte < 127:
                if pre_byte:
                    ascii_cnt += 1
                    if ascii_cnt > 1:
                        bool_ascii = True
                        break
                else:
                    pre_byte = True
            else:
                pre_byte = False
                ascii_cnt = 0

        if ascii_cnt > 5:
            bool_ascii = True

        return bool_ascii

    def create_short_table(self):
        _bodyList = collections.OrderedDict()
        for can_msg in self.all_frames:
            if can_msg.CANFrame.frame_id not in _bodyList:
                _bodyList[can_msg.CANFrame.frame_id] = collections.OrderedDict()
                _bodyList[can_msg.CANFrame.frame_id][(
                can_msg.CANFrame.frame_length,
                can_msg.CANFrame.frame_raw_data,
                can_msg.bus,
                can_msg.CANFrame.frame_ext)
                    ] = 1
            else:
                if (can_msg.CANFrame.frame_length,
                    can_msg.CANFrame.frame_raw_data,
                    can_msg.bus,
                    can_msg.CANFrame.frame_ext) not in _bodyList[can_msg.CANFrame.frame_id]:
                    _bodyList[can_msg.CANFrame.frame_id][(
                        can_msg.CANFrame.frame_length,
                        can_msg.CANFrame.frame_raw_data,
                        can_msg.bus,
                        can_msg.CANFrame.frame_ext)
                        ] = 1
                else:
                    _bodyList[can_msg.CANFrame.frame_id][(
                    can_msg.CANFrame.frame_length,
                    can_msg.CANFrame.frame_raw_data,
                    can_msg.bus,
                    can_msg.CANFrame.frame_ext)
                    ] += 1
        return _bodyList

    def find_iso_tp(self):
        message_iso = {}
        iso_list = []
        for can_msg in self.all_frames:
            if can_msg.CANFrame.frame_id not in message_iso:
                message_iso[can_msg.CANFrame.frame_id] = ISOTPMessage(can_msg.CANFrame.frame_id)

            if 1 < can_msg.CANFrame.frame_length:
                ret = message_iso[can_msg.CANFrame.frame_id].add_can(can_msg.CANFrame)
                if ret < 0:
                    del message_iso[can_msg.CANFrame.frame_id]
                elif ret == 1:
                    iso_list.append(message_iso[can_msg.CANFrame.frame_id])
                    del message_iso[can_msg.CANFrame.frame_id]
            else:
                del message_iso[can_msg.CANFrame.frame_id]
        return iso_list

    def find_uds(self, iso_list):
        uds_list = UDSMessage(self.shift)
        for message_iso in iso_list:
            uds_list.handle_message(message_iso)
        return uds_list

    def find_frags(self):
        frg_list = collections.OrderedDict()
        for can_msg in self.all_frames:
            index_bytes = self.meta_data.get(can_msg.CANFrame.frame_id, {}).get('id_index', None)
            if can_msg.CANFrame.frame_id not in frg_list:
                frg_list[can_msg.CANFrame.frame_id] = FragmentedCAN()

            if index_bytes: # We have META data
                idx1, idx2, strt = index_bytes.strip().split('-')
                idx1 = int(idx1)
                idx2 = int(idx2)
                strt = int(strt)
                frg_list[can_msg.CANFrame.frame_id].add_can_meta(can_msg.CANFrame, idx1, idx2, strt)

        return frg_list

    def find_loops(self):
        frg_list = collections.OrderedDict()
        for fid, lst in self._bodyList.iteritems():
            frg_list[fid] = FragmentedCAN()
            for (lenX, msg, bus, mod), cnt in lst.iteritems():
                frg_list[fid].add_can_loop(CANMessage.init_data(fid, lenX, [struct.unpack("!B", x)[0] for x in msg]))

        return frg_list

    def do_anal(self, format = "ALL"):
        self._bodyList = self.create_short_table()
        iso_tp_list = self.find_iso_tp()
        uds_list = self.find_uds(iso_tp_list)
        frag_list = self.find_frags()
        loops_list = self.find_loops()
        ret_str = ""

        format.upper()

        _iso_tbl = collections.OrderedDict()
        for msg in iso_tp_list:
            if msg.message_id not in _iso_tbl:
                _iso_tbl[msg.message_id] = collections.OrderedDict()
                _iso_tbl[msg.message_id][(msg.message_length, ''.join([struct.pack("!B", b) for b in msg.message_data]))] = 1
            else:
                if (msg.message_length, ''.join([struct.pack("!B", b) for b in msg.message_data])) in _iso_tbl[msg.message_id]:
                    _iso_tbl[msg.message_id][(msg.message_length, ''.join([struct.pack("!B", b) for b in msg.message_data]))] += 1
                else:
                    _iso_tbl[msg.message_id][(msg.message_length, ''.join([struct.pack("!B", b) for b in msg.message_data]))] = 1

        if format.strip() not in ["ISO","FRAG"]:
            # Print out UDS
            ret_str += "UDS Detected:\n\n"
            for fid, services in uds_list.sessions.iteritems():
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
                        data_ascii = "\n"
                        if self.is_ascii(body['response']['data']):
                            data_ascii = "\n\t\tASCII: " + self.ret_ascii(data)+"\n"
                        ret_str += "\n\tID: " + str(fid) + " Service: " + str(hex(service)) + " Sub: " + (str(
                            hex(body['sub'])) if body['sub'] else "None") + text + "\n\t\tResponse: " + data.encode('hex') + data_ascii
                    elif body['status'] == 2:
                       ret_str += "\n\tID: " + str(fid) + " Service: " + str(hex(service)) + " Sub: " + (str(
                            hex(body['sub'])) if body['sub'] else "None") + text + "\n\t\tError: " + body['response']['error']

        if format.strip() not in ["ISO","UDS"]:
            # Print detected loops
            ret_str += "\n\nDe-Fragmented frames (using loop-based detection):\n"
            local_temp = {}
            for fid, data in loops_list.iteritems():
                data.clean_build_loop()
                for message in data.messages:
                    if (fid, ''.join(struct.pack("!B", b).encode('hex') for b in message['message_data'])) not in local_temp:
                        ret_str += "\n\tID " + str(fid) + " and length " + str(message['message_length']) + "\n"
                        ret_str += "\t\tData: " + ''.join(struct.pack("!B", b).encode('hex') for b in message['message_data'])
                        if self.is_ascii(message['message_data']):
                            ret_str += "\n\t\tASCII: " + self.ret_ascii(''.join(struct.pack("!B", b) for b in message['message_data'])) + "\n\n"
                        local_temp[(fid, ''.join(struct.pack("!B", b).encode('hex') for b in message['message_data']))] = None

            # Print detected fragments
            ret_str += "\n\nDe-Fragmented frames (using user's META data):\n"
            local_temp = {}
            for fid, data in frag_list.iteritems():
                data.clean_build_meta()
                for message in data.messages:
                    if (fid, ''.join(struct.pack("!B", b).encode('hex') for b in message['message_data'])) not in local_temp:
                        ret_str += "\n\tID " + str(fid) + " and length " + str(message['message_length']) + "\n"
                        ret_str += "\t\tData: " + ''.join(struct.pack("!B", b).encode('hex') for b in message['message_data'])
                        if self.is_ascii(message['message_data']):
                            ret_str += "\n\t\tASCII: " + self.ret_ascii(''.join(struct.pack("!B", b) for b in message['message_data'])) + "\n\n"
                        local_temp[(fid, ''.join(struct.pack("!B", b).encode('hex') for b in message['message_data']))] = None


        if format.strip() not in ["UDS","FRAG"]:
            # Print out ISOTP messages
            ret_str += "ISO TP Messages:\n\n"
            for fid, lst in _iso_tbl.iteritems():
                ret_str += "\tID: " + str(fid) + "\n"
                for (lenX, msg), cnt in lst.iteritems():
                    ret_str += "\t\tDATA: " + msg.encode('hex')
                    if self.is_ascii([struct.unpack("!B", x)[0] for x in msg]):
                        ret_str += "\n\t\tASCII: " + self.ret_ascii(msg)
                    ret_str += "\n"

        return ret_str

    def do_dump_replay(self, name):
        _name = None
        try:
            _name = open(name.strip(), 'w')
            for can_msg in self.all_frames:
                _name.write(str(can_msg.CANFrame.frame_id) + ":" + str(can_msg.CANFrame.frame_length) + ":" + can_msg.CANFrame.frame_raw_data.encode('hex') + "\n")
            _name.close()
        except Exception as e:
            self.dprint(2, "can't open log")
            return str(e)
        return "Saved into " + name.strip()


    def do_dump_csv(self, name):
        self._bodyList = self.create_short_table()
        _name = None
        try:
            _name = open(name.strip(), 'w')
            _name.write("BUS,ID,LENGTH,MESSAGE,ASCII,COMMENT,COUNT\n")
            for fid, lst in self._bodyList.iteritems():
                for (len, msg, bus, mod), cnt in lst.iteritems():
                    if self.is_ascii([struct.unpack("B", x)[0] for x in msg]):
                        data_ascii = '"' + self.ret_ascii(msg) + '"'
                    else:
                        data_ascii = ""
                    _name.write(
                        str(bus) + "," + str(fid) + "," + str(len) + "," + msg.encode('hex') + ',' + data_ascii + ',' +\
                        "\"" + self.meta_data.get(fid, {}).get('id_descr', "") + "\"" + ',' + str(cnt) + "\n"
                    )
        except Exception as e:
            self.dprint(2, "can't open log")
            return str(e)
        return "Saved into " + name.strip()

    def do_print(self):
        self._bodyList = self.create_short_table()
        table = "\n"
        rows = [['BUS', 'ID', 'LENGTH', 'MESSAGE', 'ASCII', 'DESCR', 'COUNT']]
        # http://stackoverflow.com/questions/3685195/line-up-columns-of-numbers-print-output-in-table-format
        for fid, lst in self._bodyList.iteritems():
            for (lenX, msg, bus, mod), cnt in lst.iteritems():
                if self.is_ascii([struct.unpack("B", x)[0] for x in msg]):
                    data_ascii = self.ret_ascii(msg)
                else:
                    data_ascii = "  "
                rows.append([str(bus),str(fid), str(lenX), msg.encode('hex'), data_ascii, self.meta_data.get(fid, {}).get('id_descr', "   "), str(cnt)])

        cols = zip(*rows)
        col_widths = [ max(len(value) for value in col) for col in cols ]
        format_table = ' '.join(['%%-%ds' % width for width in col_widths ])
        for row in rows:
            table += format_table % tuple(row) + "\n"
        table += ""
        return table

    def do_clean(self):
        self._alert = False
        self.all_frames = []
        return ""

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if can_msg.CANData:
            self.all_frames.append(can_msg)

        return can_msg
