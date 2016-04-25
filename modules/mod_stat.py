from libs.module import *
from libs.uds import *
from libs.frag import *
import json
import re
import collections
import ast


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

    def get_status(self):
        return "Current status: " + str(self._active) + "\nSniffed frames: " + str(len(self.all_frames))+"\nDiff mode: " + str(self._diff) +\
            "\nSniffed in Diff mode: " + str(len(self.all_diff_frames))

    def do_init(self, params):
        self.all_frames = []
        self.all_diff_frames = []
        self.meta_data = {}
        self._bodyList = collections.OrderedDict()
        self._diff = False

        self.shift = params.get('uds_shift', 8)

        if 'meta_file' in params:
            self.dprint(1, self.do_load_meta(params['meta_file']))

        self._cmdList['p'] = ["Print current table", 0, "", self.do_print, True]
        self._cmdList['a'] = ["Analyses of captured traffic", 1, "<UDS|ISO|FRAG|ALL(defaut)>", self.do_anal, True]
        self._cmdList['D'] = ["Enable/Disable Diff mode", 0, "", self.enable_diff, True]
        self._cmdList['I'] = ["Print Diff frames", 1, " [COUNT filter (default none, put number)] ", self.print_diff, False]
        self._cmdList['N'] = ["Print Diff frames (new ID only)", 1, "[COUNT filter (default none, put number)]", self.print_diff_id, False]
        self._cmdList['Y'] = ["Dump Diff in replay format", 1, " <filename> ", self.print_dump_diff, False]
        self._cmdList['c'] = ["Clean table, remove alerts", 0, "", self.do_clean, True]
        self._cmdList['i'] = ["Meta-data: add description for frames", 1, "<ID>, <data regex ASCII HEX>, <description>", self.do_add_meta_descr_data, True]
        self._cmdList['l'] = ["Load meta-data", 1, "<filename>", self.do_load_meta, True]
        self._cmdList['z'] = ["Save meta-data", 1, "<filename>", self.do_save_meta, True]
        self._cmdList['r'] = ["Dump ALL in replay format", 1, " <filename>", self.do_dump_replay, True]
        self._cmdList['d'] = ["Dump STAT in CSV format", 1, " <filename>", self.do_dump_csv, True]

    def do_add_meta_descr_data(self, input_params):
        try:
            fid, body, descr = input_params.split(',')
            if fid.strip().find('0x') == 0:
                num_fid = int(fid, 16)
            else:
                num_fid = int(fid)
            if 'description' not in self.meta_data:
                self.meta_data['description'] = {}

            self.meta_data['description'][(num_fid, body.strip().upper())] = descr

            return "Description data has been added"
        except Exception as e:
            return "Description data META error: " + str(e)

    def get_meta_descr(self, fid, msg):
        descrs = self.meta_data.get('description', {})
        for (key, body) in list(descrs.keys()):
            if fid == key:
                if(re.match(body, self.get_hex(msg), re.IGNORECASE)):
                    return str(descrs[(key, body)])
        return "  "


    def do_load_meta(self, filename):
        try:
            data = ""
            with open(filename.strip(), "r") as ins:
                for line in ins:
                    data += line
            self.meta_data = ast.literal_eval(data)

        except Exception as e:
            return "Can't load META: " + str(e)
        return "Loaded META from " + filename

    def do_save_meta(self, filename):
        try:
            _file = open(filename.strip(), 'w')
            _file.write(str(self.meta_data))
            _file.close()
        except Exception as e:
            return "Can't save META: " + str(e)
        return "Saved META to " + filename

    # Detect ASCII data
    @staticmethod
    def ret_ascii(text_array):
        return_str = ""
        for byte in text_array:
            if 31 < byte < 127:
                return_str += chr(byte)
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

    @staticmethod
    def create_short_table(input_frames):
        _bodyList = collections.OrderedDict()
        for can_msg in input_frames:
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
        for fid, lst in self._bodyList.items():
            frg_list[fid] = FragmentedCAN()
            for (lenX, msg, bus, mod), cnt in lst.items():
                frg_list[fid].add_can_loop(CANMessage.init_data(fid, lenX, msg))

        return frg_list

    def do_anal(self, format = "ALL"):
        if self._diff:
            self.enable_diff()

        self._bodyList = self.create_short_table(self.all_frames)
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
                _iso_tbl[msg.message_id][(msg.message_length,  bytes(msg.message_data))] = 1
            else:
                if (msg.message_length, bytes(msg.message_data)) in _iso_tbl[msg.message_id]:
                    _iso_tbl[msg.message_id][(msg.message_length,  bytes(msg.message_data))] += 1
                else:
                    _iso_tbl[msg.message_id][(msg.message_length, bytes(msg.message_data))] = 1

        if format.strip() not in ["ISO","FRAG"]:
            # Print out UDS
            ret_str += "UDS Detected:\n\n"
            for fid, services in uds_list.sessions.items():
                for service, body in services.items():
                    text = " (N/A) "
                    if service in UDSMessage.services_base:
                        for sub in UDSMessage.services_base[service]:
                            if list(sub.keys())[0] == body['sub'] or None:
                                text = " (" + list(sub.values())[0] + ") "
                        if text == " (N/A) ":
                            text = " (" + list(UDSMessage.services_base[service][0].values())[0] + ") "
                    if body['status'] == 1:
                        data =  body['response']['data']
                        data_ascii = "\n"
                        if self.is_ascii(body['response']['data']):
                            data_ascii = "\n\t\tASCII: " + self.ret_ascii(data)+"\n"
                        ret_str += "\n\tID: " + hex(fid) + " Service: " + str(hex(service)) + " Sub: " + (str(
                            hex(body['sub'])) if body['sub'] else "None") + text + "\n\t\tResponse: " + self.get_hex(bytes(data)) + data_ascii
                    elif body['status'] == 2:
                       ret_str += "\n\tID: " + hex(fid) + " Service: " + str(hex(service)) + " Sub: " + (str(
                            hex(body['sub'])) if body['sub'] else "None") + text + "\n\t\tError: " + body['response']['error']

        if format.strip() not in ["ISO", "UDS"]:
            # Print detected loops
            ret_str += "\n\nDe-Fragmented frames (using loop-based detection):\n"
            local_temp = {}
            for fid, data in loops_list.items():
                data.clean_build_loop()
                for message in data.messages:
                    if (fid, bytes(message['message_data'])) not in local_temp:
                        ret_str += "\n\tID " + hex(fid) + " and length " + str(message['message_length']) + "\n"
                        ret_str += "\t\tData: " + self.get_hex(bytes(message['message_data']))
                        if self.is_ascii(message['message_data']):
                            ret_str += "\n\t\tASCII: " + self.ret_ascii(bytes(message['message_data'])) + "\n\n"
                        local_temp[(fid, bytes(message['message_data']))] = None

        if format.strip() not in ["UDS","FRAG"]:
            # Print out ISOTP messages
            ret_str += "\nISO TP Messages:\n\n"
            for fid, lst in _iso_tbl.items():
                ret_str += "\tID: " + hex(fid) + "\n"
                for (lenX, msg), cnt in lst.items():
                    ret_str += "\t\tDATA: " + self.get_hex(msg)
                    if self.is_ascii(msg):
                        ret_str += "\n\t\tASCII: " + self.ret_ascii(msg)
                    ret_str += "\n"

        return ret_str

    def print_dump_diff(self, name):
        table1 = self.create_short_table(self.all_frames)
        try:
            _name = open(name.strip(), 'w')
            for can_msg in self.all_diff_frames:
                if can_msg.CANFrame.frame_id not in list(table1.keys()):
                    _name.write(str(can_msg.CANFrame.frame_id) + ":" + str(can_msg.CANFrame.frame_length) + ":" + self.get_hex(can_msg.CANFrame.frame_raw_data) + "\n")
                else:
                    neq = True
                    for (len2, msg, bus, mod), cnt in table1[can_msg.CANFrame.frame_id].items():
                        if msg == can_msg.CANFrame.frame_raw_data:
                            neq = False
                    if neq:
                        _name.write(hex(can_msg.CANFrame.frame_id) + ":" + str(can_msg.CANFrame.frame_length) + ":" + self.get_hex(can_msg.CANFrame.frame_raw_data) + "\n")
            _name.close()
        except Exception as e:
            self.dprint(2, "can't open log")
            return str(e)
        return "Saved into " + name.strip()

    def do_dump_replay(self, name):

        try:
            _name = open(name.strip(), 'w')
            for can_msg in self.all_frames:
                _name.write(hex(can_msg.CANFrame.frame_id) + ":" + str(can_msg.CANFrame.frame_length) + ":" + self.get_hex(can_msg.CANFrame.frame_raw_data) + "\n")
            _name.close()
        except Exception as e:
            self.dprint(2, "can't open log")
            return str(e)
        return "Saved into " + name.strip()


    def do_dump_csv(self, name):
        self._bodyList = self.create_short_table(self.all_frames)
        try:
            _name = open(name.strip(), 'w')
            _name.write("BUS,ID,LENGTH,MESSAGE,ASCII,COMMENT,COUNT\n")
            for fid, lst in self._bodyList.items():
                for (len, msg, bus, mod), cnt in lst.items():
                    if self.is_ascii(msg):
                        data_ascii = '"' + self.ret_ascii(msg) + '"'
                    else:
                        data_ascii = ""
                    _name.write(
                        str(bus) + "," + hex(fid) + "," + str(len) + "," + self.get_hex(msg) + ',' + data_ascii + ',' +\
                        "\"" + self.get_meta_descr(fid, msg) + "\"" + ',' + str(cnt) + "\n"
                    )
        except Exception as e:
            self.dprint(2, "can't open log")
            return str(e)
        return "Saved into " + name.strip()

    def print_diff(self, count = 0):
        return self.print_diff_orig(0, int(count))

    def print_diff_id(self, count = 0):
        return self.print_diff_orig(1, int(count))

    def print_diff_orig(self, mode = 0, count = 0):
        if not self._diff:
            return "Error: Diff mode disabled..."
        table1 = self.create_short_table(self.all_frames)
        table2 = self.create_short_table(self.all_diff_frames)
        table = ""
        rows = [['BUS', 'ID', 'LENGTH', 'MESSAGE', 'ASCII', 'DESCR', 'COUNT']]
        for fid2, lst2 in table2.items():
            if fid2 not in list(table1.keys()):

                for (lenX, msg, bus, mod), cnt in lst2.items():
                    if self.is_ascii(msg):
                        data_ascii = self.ret_ascii(msg)
                    else:
                        data_ascii = "  "
                    if count == 0 or count == cnt:
                        rows.append([str(bus),hex(fid2), str(lenX), self.get_hex(msg), data_ascii, self.get_meta_descr(fid2, msg), str(cnt)])
            elif mode == 0:
                for (lenX, msg, bus, mod), cnt in lst2.items():

                    if (lenX, msg, bus, mod) not in  table1[fid2]:
                        if self.is_ascii(msg):
                            data_ascii = self.ret_ascii(msg)
                        else:
                            data_ascii = "  "
                        if count == 0 or count == cnt:
                            rows.append([str(bus),hex(fid2), str(lenX), self.get_hex(msg), data_ascii, self.get_meta_descr(fid2, msg), str(cnt)])

        cols = list(zip(*rows))
        col_widths = [max(len(value) for value in col) for col in cols]
        format_table = '    '.join(['%%-%ds' % width for width in col_widths ])
        for row in rows:
            table += format_table % tuple(row) + "\n"
        table += "\n"
        return table

    def enable_diff(self):
        if self._diff:
            self.all_frames += self.all_diff_frames
            self.all_diff_frames = []
            #self._cmdList['p'][4] = True
            self._cmdList['a'][4] = True
            self._cmdList['r'][4] = True
            self._cmdList['d'][4] = True
            self._cmdList['I'][4] = False
            self._cmdList['N'][4] = False
            self._cmdList['Y'][4] = False
        else:
            #self._cmdList['p'][4] = False
            self._cmdList['a'][4] = False
            self._cmdList['r'][4] = False
            self._cmdList['d'][4] = False
            self._cmdList['I'][4] = True
            self._cmdList['N'][4] = True
            self._cmdList['Y'][4] = True
        self._diff = not self._diff
        return "Diff mode: "+str(self._diff)


    def do_print(self):
        self._bodyList = self.create_short_table(self.all_frames)
        table = "\n"
        rows = [['BUS', 'ID', 'LENGTH', 'MESSAGE', 'ASCII', 'DESCR', 'COUNT']]
        # http://stackoverflow.com/questions/3685195/line-up-columns-of-numbers-print-output-in-table-format
        for fid, lst in self._bodyList.items():
            for (lenX, msg, bus, mod), cnt in lst.items():
                if self.is_ascii(msg):
                    data_ascii = self.ret_ascii(msg)
                else:
                    data_ascii = "  "
                rows.append([str(bus),hex(fid), str(lenX), self.get_hex(msg), data_ascii, self.get_meta_descr(fid, msg), str(cnt)])

        cols = list(zip(*rows))
        col_widths = [ max(len(value) for value in col) for col in cols ]
        format_table = '    '.join(['%%-%ds' % width for width in col_widths ])
        for row in rows:
            table += format_table % tuple(row) + "\n"
        table += ""
        return table

    def do_clean(self):
        self.all_frames = []
        self.all_diff_frames = []
        self._diff = False
        self._cmdList['a'][4] = True
        self._cmdList['r'][4] = True
        self._cmdList['d'][4] = True
        self._cmdList['I'][4] = False
        self._cmdList['N'][4] = False
        self._cmdList['Y'][4] = False
        return "Buffers cleaned!"

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if can_msg.CANData:
            if not self._diff:
                self.all_frames.append(can_msg)
            else:
                self.all_diff_frames.append(can_msg)

        return can_msg
