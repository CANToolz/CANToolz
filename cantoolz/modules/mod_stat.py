from cantoolz.uds import *
from cantoolz.frag import *
from cantoolz.replay import *
import bitstring
import re
import collections
import ast
import time
from cantoolz.correl import *
import operator


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

    def do_activate(self, def_in = 0, mode = -1):
        if mode == -1:
            self._active = not self._active
        elif mode == 0:
            self._active = False
        else:
            self._active = True
        self.all_frames[-1]['buf'].add_timestamp()

        return "Active status: " + str(self._active)

    def get_status(self, def_in = 0):
        return "Current status: " + "\nActive STATCHECK running:" + str(self._active_check) + "\nSniffed frames (overall): " + str(self.get_num(-1))+"\nCurrent BUFF: index - " + str(self._index) + " name - " + self.all_frames[self._index]['name'] + \
               "\nAll buffers: \n\t" + \
            '\n\t'.join([buf['name'] + "\n\t\tindex: " + str(cnt) + ' sniffed: ' + str(len(buf['buf'])) for buf,cnt in zip(self.all_frames,range(0,len(self.all_frames)))])

    def do_init(self, params):
        self.all_frames = [{'name':'start_buffer','buf':Replay()}]
        self.dump_stat = Replay()
        self._index = 0
        self._rep_index = None
        self.meta_data = {}
        self._bodyList = collections.OrderedDict()
        self.shift = params.get('uds_shift', 8)
        self.subnet = Subnet(lambda stream: Separator(SeparatedMessage.builder))
        self.data_set = {}
        self._train_buffer = -1
        self._action = threading.Event()
        self._action.clear()
        self._last = 0
        self._full = 1
        self._need_status = False
        self._stat_resend = None
        self._active_check = False

        if 'meta_file' in params:
            self.dprint(1, self.do_load_meta(0, params['meta_file']))

        self._cmdList['p'] = Command("Print current table",1, "[index]", self.do_print, True)

        self._cmdList['a'] = Command("Analysis of captured traffic", 1, "<UDS|ISO|FRAG|ALL(defaut)>,[buffer index]", self.do_anal, True)
        self._cmdList['u'] = Command("    - UDS shift value",1,"[shift value]", self.change_shift, True)

        self._cmdList['D'] = Command("Switch sniffing to a new buffer", 1, "[name]", self.new_diff, True)
        self._cmdList['I'] = Command("Print Diff between two buffers", 1, "[buffer index 1], [buffer index 2], [uniq values max]", self.print_diff, True)
        self._cmdList['N'] = Command("Print Diff between two buffers (new ID only)", 1, "[buffer index 1], [buffer index 2]", self.print_diff_id, True)

        self._cmdList['Y'] = Command("Dump Diff in replay format", 1, "<filename>,[buffer index ,buffer index], [uniq values max]", self.print_dump_diff, True)
        self._cmdList['y'] = Command("Dump Diff in replay format (new ID)", 1, "<filename>,[buffer index 1] , [buffer index 2]", self.print_dump_diff_id, True)
        self._cmdList['F'] = Command("Search ID in all buffers", 1, "<ID>", self.search_id, True)

        self._cmdList['train'] = Command("STATCHECK: profiling on normal traffic (EXPEREMENTAL)", 1, "[buffer index]", self.train, True)
        self._cmdList['check'] = Command("STATCHECK: find abnormalities on 'event' traffic  (EXPEREMENTAL)", 1, "[buffer index]", self.find_ab, True)
        self._cmdList['act'] = Command("STATCHECK: find action frame  (EXPEREMENTAL)", 0, "", self.act_detect, False)
        self._cmdList['dump_st'] = Command("STATCHECK: dump abnormalities in Replay format  (EXPEREMENTAL)", 1, "<filename>", self.dump_ab, False)

        self._cmdList['load'] = Command("Load Replay dumps from files into buffers", 1, "filename1[,filename2,...] ", self.load_rep, True)

        self._cmdList['change'] = Command("Detect changes for ECU (EXPEREMENTAL)", 1, "[buffer index][, max uniq. values]", self.show_change, True)
        self._cmdList['detect'] = Command("Detect changes for ECU by control FRAME (EXPEREMENTAL)", 1, "<ECU ID:HEX_DATA>[,buffer index]", self.show_detect, True)
        self._cmdList['show'] = Command("Show detected amount of fields for all ECU (EXPEREMENTAL)", 1, "[buffer index]", self.show_fields, True)
        self._cmdList['fields'] = Command("Show values in fields for chosen ECU (EXPEREMENTAL)", 1, "<ECU ID>[, hex|bin|int [, buffer index ]]", self.show_fields_ecu, True)

        self._cmdList['c'] = Command("Clean table, remove buffers", 0, "", self.do_clean, True)

        self._cmdList['i'] = Command("Meta-data: add description for frames", 1, "<ID>, <data regex ASCII HEX>, <description>", self.do_add_meta_descr_data, True)
        self._cmdList['bits'] = Command("Meta-data: bits fields description", 1, "<ID>, <LEN>, <TYPE>:<LAST BIT INDEX>:<DESCRIPTION>[,...]", self.do_add_meta_bit_data, True)
        self._cmdList['l'] = Command("Load meta-data", 1, "<filename>", self.do_load_meta, True)
        self._cmdList['z'] = Command("Save meta-data", 1, "<filename>", self.do_save_meta, True)
        self._cmdList['r'] = Command("Dump buffer (if index is empty then all) in replay format", 1, " <filename>, [index]", self.do_dump_replay, True)
        self._cmdList['d2'] = Command("Dump buffer (if index is empty then all) in CSV format", 1, " <filename>, [index]", self.do_dump_csv2, True)
        self._cmdList['d'] = Command("Dump STATS for buffer (if index is empty then all) in CSV format", 1, " <filename>, [index]", self.do_dump_csv, True)
        self._cmdList['g'] = Command("Get DELAY value for gen_ping/gen_fuzz (EXPERIMENTAL)",1,"<Bus SPEED in Kb/s>", self.get_delay, True)


    def get_delay(self, def_in, speed):
        _speed = float(speed)*1024
        curr_1 = len(self.all_frames[self._index]['buf'])
        time.sleep(3)
        curr_2 = len(self.all_frames[self._index]['buf'])
        diff = curr_2 - curr_1
        speed = int((diff * 80)/3)
        delay = 1/int((_speed - speed)/80)
        return "Avrg. delay: " + str(delay)

    def change_shift(self, def_in, val):
        if val.strip()[0:2] == '0x':
            value = int(val,16)
        else:
            value = int(val)
        self.shift = value
        return "UDS shift: " + hex(self.shift)

    def do_add_meta_bit_data(self, def_in, input_params):
        try:
            fid, leng = input_params.split(',')[0:2]
            descr = input_params.split(',')[2:]
            if fid.strip().find('0x') == 0:
                num_fid = int(fid, 16)
            else:
                num_fid = int(fid)
            if 'bits' not in self.meta_data:
                self.meta_data['bits'] = {}
            bitsX = []
            for dsc in descr:
                bitsX.append({ dsc.split(":")[0].strip():{int(dsc.split(":")[1]):dsc.split(":")[2].strip()}})
            self.meta_data['bits'][(num_fid, int(leng))] = bitsX

            return "Fields data has been added"
        except Exception as e:
            return "Fields data META error: " + str(e)

    def do_add_meta_descr_data(self, def_in, input_params):
        try:
            fid, body, descr = input_params.split(',')
            if fid.strip().find('0x') == 0:
                num_fid = int(fid, 16)
            else:
                num_fid = int(fid)
            if 'description' not in self.meta_data:
                self.meta_data['description'] = {}

            self.meta_data['description'][(num_fid, body.strip().upper())] = descr.strip()

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

    def get_meta_bits(self, fid, len):
        return self.meta_data.get('bits', {}).get((fid, len), None)

    def get_meta_all_bits(self):
        return self.meta_data.get('bits', {})

    def do_load_meta(self, def_in, filename):
        try:
            data = ""
            with open(filename.strip(), "r") as ins:
                for line in ins:
                    data += line
            self.meta_data = ast.literal_eval(data)

        except Exception as e:
            return "Can't load META: " + str(e)
        return "Loaded META from " + filename

    def do_save_meta(self, def_in, filename):
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

    def get_num(self,_index = -1):
        count = 0
        if _index == -1:
            for buf in self.all_frames:
                count += len(buf['buf'])
        else:
            count = len(self.all_frames[_index]['buf'])

        return count

    @staticmethod
    def create_short_table(input_frames):
        _bodyList = collections.OrderedDict()
        for timestmp, can_msg in input_frames:
            #print(len(input_frames))
            #print(can_msg.CANData)

            if can_msg.CANData:
                #print(can_msg.CANFrame)
                #print(can_msg.CANFrame.frame_raw_data)
                #print()
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

    def find_iso_tp(self, in_list):
        message_iso = {}
        iso_list = []
        for timestmp, can_msg in in_list:
            if can_msg.CANData:
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

    def find_loops(self):
        frg_list = collections.OrderedDict()
        for fid, lst in self._bodyList.items():
            frg_list[fid] = FragmentedCAN()
            for (lenX, msg, bus, mod), cnt in lst.items():
                frg_list[fid].add_can_loop(CANMessage.init_data(fid, lenX, msg))

        return frg_list

    def do_anal(self, def_in, format = "ALL"):

        format.upper()

        params = format.split(",")
        if len(params) == 1:
            _format = params[0].strip()
            _index  = -1
        else:
           _format = params[0].strip()
           _index  = int(params[1])
        temp_buf = Replay()
        if _index == -1:
            for buf in self.all_frames:
                temp_buf = temp_buf + buf['buf']
        else:
            temp_buf = self.all_frames[_index]['buf']

        self._bodyList = self.create_short_table(temp_buf)
        iso_tp_list = self.find_iso_tp(temp_buf)
        uds_list = self.find_uds(iso_tp_list)
        loops_list = self.find_loops()
        ret_str = ""

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

        if _format.strip() not in ["ISO","FRAG"]:
            # Print out UDS
            ret_str += "UDS Detected:\n\n"
            for fid, services in uds_list.sessions.items():
                for service, sub in services.items():
                    for sub_id, body in sub.items():
                        text = " (UNKNOWN) "
                        if service in UDSMessage.services_base:
                            serv_name = UDSMessage.services_base[service].get(sub_id,UDSMessage.services_base[service].get(None,'UNKNOWN'))
                            text = " (" + serv_name + ") "

                        if body['status'] == 1:
                            data =  body['response']['data']
                            data2 = body['data']
                            data_ascii = ""
                            data_ascii2 = ""
                            if self.is_ascii(data2):
                                data_ascii2 = "\n\t\tASCII: " + self.ret_ascii(data2)+"\n"
                            if self.is_ascii(body['response']['data']):
                                data_ascii = "\n\t\tASCII: " + self.ret_ascii(data)+"\n"
                            ret_str += "\n\tID: " + hex(fid) + " Service: " + str(hex(service)) + " Sub: " + ((str(
                                hex(sub_id))) if sub_id < 0x100 else " NO SUB ") + text + "\n\t\tRequest: " + self.get_hex(bytes(data2)) + data_ascii2 +\
                                       "\n\t\tResponse: " + self.get_hex(bytes(data)) + data_ascii + "\n"
                        elif body['status'] == 2:
                            data2 = body['data']
                            data_ascii2 = ""
                            if self.is_ascii(data2):
                                data_ascii2 = "\n\t\tASCII: " + self.ret_ascii(data2)+"\n"
                            ret_str += "\n\tID: " + hex(fid) + " Service: " + str(hex(service)) + " Sub: " + ((str(
                                hex(sub_id))) if sub_id < 0x100 else " (ALTERNATIVE INTERPRETATION if NO SUB) ")  + text + "\n\t\tRequest: " + self.get_hex(bytes(data2)) + data_ascii2 +\
                                      "\n\t\tError: " + body['response']['error'] + "\n"

        if _format.strip() not in ["ISO", "UDS"]:
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

        if _format.strip() not in ["UDS","FRAG"]:
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

    def search_id(self, def_in, idf):
        idf = int(idf) if not idf.strip()[0:2] == '0x' else int(idf,16)
        table = "Search for " + hex(idf) + "\n"
        rows = []
        for buf in self.all_frames:
            rows.append(['Dump:', buf['name'], ' ',  ' ', ' ', ' ', ' '])
            rows.append(['BUS', 'ID', 'LENGTH', 'MESSAGE', 'ASCII', 'DESCR', 'COUNT'])
            short = self.create_short_table(buf['buf'])
            if idf in short:
                 for (lenX, msg, bus, mod), cnt in short[idf].items():
                    if self.is_ascii(msg):
                        data_ascii = self.ret_ascii(msg)
                    else:
                        data_ascii = "  "
                    rows.append([str(bus),hex(idf), str(lenX), self.get_hex(msg), data_ascii, self.get_meta_descr(idf, msg), str(cnt)])
        cols = list(zip(*rows))
        col_widths = [max(len(value) for value in col) for col in cols]
        format_table = '    '.join(['%%-%ds' % width for width in col_widths ])
        for row in rows:
            table += format_table % tuple(row) + "\n"
        table += "\n"
        return table

    def print_dump_diff(self, def_in,name):
        return self.print_dump_diff_(name, 0)

    def print_dump_diff_id(self, def_in,name):
        return self.print_dump_diff_(name, 1)

    def print_dump_diff_(self, name, mode = 0):
        inp = name.split(",")
        if len(inp) == 4:
            name = inp[0].strip()
            idx1 = int(inp[1])
            idx2 = int(inp[2])
            rang = int(inp[3])
        elif len(inp) == 3:
            name = inp[0].strip()
            idx1 = int(inp[1])
            idx2 = int(inp[2])
            rang = 8 * 256
        else:
            name = inp[0].strip()
            idx2 = self._index
            idx1 = self._index - 1 if self._index - 1 >=0 else 0
            rang = 8 * 256

        table1 = self.create_short_table(self.all_frames[idx1]['buf'])
        tblDif = self.all_frames[idx2]['buf'] + self.all_frames[idx1]['buf']
        table2 = self.create_short_table(tblDif)
        try:
            #_name = open(name, 'w')
            dump = Replay()
            dump.add_timestamp()
            tms = 0.0
            for timestmp, can_msg in self.all_frames[idx2]['buf']:
                if can_msg.CANData:
                    if tms == 0.0:
                        tms = timestmp
                    if can_msg.CANFrame.frame_id not in list(table1.keys()):
                        dump.append_time(timestmp - tms, can_msg)
                    elif mode == 0 and len(table2[can_msg.CANFrame.frame_id]) <= rang:
                        neq = True
                        for (len2, msg, bus, mod), cnt in table1[can_msg.CANFrame.frame_id].items():
                            if msg == can_msg.CANFrame.frame_raw_data:
                                neq = False
                        if neq:
                            dump.append_time(timestmp - tms,can_msg)
                elif can_msg.debugData:
                    dump.add_timestamp()
                    tms = 0.0
            dump.save_dump(name)
        except Exception as e:
            self.dprint(2, "can't open log")
            return str(e)
        return "Saved into " + name

    def do_dump_replay(self, def_in, name):
        inp = name.split(",")
        if len(inp) == 2:
            name = inp[0].strip()
            idx1 = int(inp[1])
        else:
            name = inp[0].strip()
            idx1 = -1

        temp_buf = Replay()
        if idx1 == -1:
            for buf in self.all_frames:
                temp_buf = temp_buf + buf['buf']
        else:
            temp_buf = self.all_frames[idx1]['buf']

        try:
            temp_buf.save_dump(name)
        except Exception as e:
            self.dprint(2, "can't open log")
            return str(e)
        return "Saved into " + name.strip()

    def esacpe_csv(self, _string):
        return '"'+_string.replace('"', '""')+'"'

    def do_dump_csv2(self, def_in, name):
        inp = name.split(",")
        if len(inp) == 2:
            name = inp[0].strip()
            idx1 = int(inp[1])
        else:
            name = inp[0].strip()
            idx1 = -1

        temp_buf = Replay()
        if idx1 == -1:
            for buf in self.all_frames:
                temp_buf = temp_buf + buf['buf']
        else:
            temp_buf = self.all_frames[idx1]['buf']

        self._bodyList = self.create_short_table(temp_buf)
        #if 1==1:
        try:
            descr = ""
            bitzx = self.get_meta_all_bits()
            for (fid,flen), body in bitzx.items():
                for bt in body:
                    descr += "," + str(fid) + "_" + list(list(bt.values())[0].values())[0]

            _name = open(name.strip(), 'w')
            _name.write("TIME,BUS,ID,LENGTH,DATA_BYTE1,DATA_BYTE2,DATA_BYTE3,DATA_BYTE4,DATA_BYTE5,DATA_BYTE6,DATA_BYTE7,DATA_BYTE8,ASCII,COMMENT" + descr + "\n")

            for times, msg in temp_buf._stream:
                if not msg.debugData and msg.CANData:


                    data = msg.CANFrame.frame_data[:msg.CANFrame.frame_length] + ([0] * (8 - msg.CANFrame.frame_length))

                    data_ascii = self.esacpe_csv(self.ret_ascii(msg.CANFrame.frame_raw_data)) if self.is_ascii(msg.CANFrame.frame_raw_data) else "  "

                    format_ = self.get_meta_bits(msg.CANFrame.frame_id,msg.CANFrame.frame_length)

                    filds = ""
                    if  format_:
                        idx_0 = 0
                        for  bitz in format_:
                            fmt = list(bitz.keys())[0]
                            idx = list(list(bitz.values())[0].keys())[0]
                            filds += "," + self.get_data_in_format(msg.CANFrame.frame_raw_data, idx_0, idx, fmt)
                            idx_0 = idx

                    _name.write(
                        str(round(times, 4)) + ',' +
                        str(msg.bus) + ',' +
                        str(msg.CANFrame.frame_id) + ',' +
                        str(msg.CANFrame.frame_length) + ',' +
                        str(data[0]) + ',' +
                        str(data[1]) + ',' +
                        str(data[2]) + ',' +
                        str(data[3]) + ',' +
                        str(data[4]) + ',' +
                        str(data[5]) + ',' +
                        str(data[6]) + ',' +
                        str(data[7]) + ',' +
                        data_ascii + ',' +
                        self.get_meta_descr(msg.CANFrame.frame_id, msg.CANFrame.frame_raw_data) + filds + "\n"
                    )

            _name.close()
        except Exception as e:
            self.dprint(2, "can't open log")
            return str(e)
        return "Saved into " + name.strip()

    def do_dump_csv(self, def_in, name):
        inp = name.split(",")
        if len(inp) == 2:
            name = inp[0].strip()
            idx1 = int(inp[1])
        else:
            name = inp[0].strip()
            idx1 = -1

        temp_buf = Replay()
        if idx1 == -1:
            for buf in self.all_frames:
                temp_buf = temp_buf + buf['buf']
        else:
            temp_buf = self.all_frames[idx1]['buf']

        self._bodyList = self.create_short_table(temp_buf)
        try:
            _name = open(name.strip(), 'w')
            _name.write("BUS,ID,LENGTH,MESSAGE,ASCII,COMMENT,COUNT\n")
            for fid, lst in self._bodyList.items():
                for (lenX, msg, bus, mod), cnt in lst.items():

                    format_ = self.get_meta_bits(fid,lenX)
                    if not format_:
                        if self.is_ascii(msg):
                            data_ascii = self.esacpe_csv(self.ret_ascii(msg))
                        else:
                            data_ascii = "  "
                        _name.write(
                        str(bus) + "," + hex(fid) + "," + str(lenX) + "," + self.get_hex(msg) + ',' + data_ascii + ',' +\
                        "\"" + self.esacpe_csv(self.get_meta_descr(fid, msg)) + "\"" + ',' + str(cnt) + "\n"
                        )
                    else:
                        idx_0 = 0
                        msg_s = ""
                        for  bitz in format_:
                            fmt = list(bitz.keys())[0]
                            idx = list(list(bitz.values())[0].keys())[0]
                            descr = list(list(bitz.values())[0].values())[0]
                            msg_s += descr + ": " + self.get_data_in_format(msg, idx_0, idx, fmt) + " "
                            idx_0 = idx
                        _name.write(
                        str(bus) + "," + hex(fid) + "," + str(lenX) + "," + msg_s + ',' + " " + ',' +\
                        "\"" + self.esacpe_csv(self.get_meta_descr(fid, msg)) + "\"" + ',' + str(cnt) + "\n"
                        )
            _name.close()
        except Exception as e:
            self.dprint(2, "can't open log")
            return str(e)
        return "Saved into " + name.strip()

    def print_diff(self, def_in, inp = ""):
        inp = inp.split(",")
        if len(inp) == 3:
            idx1 = int(inp[0])
            idx2 = int(inp[1])
            rang = int(inp[2])
        elif len(inp) == 2:
            idx1 = int(inp[0])
            idx2 = int(inp[1])
            rang = 8 * 256
        else:
            idx2 = self._index
            idx1 = self._index - 1 if self._index - 1 >=0 else 0
            rang = 8 * 256

        return self.print_diff_orig(0, idx1, idx2, rang)

    def print_diff_id(self, def_in, inp = ""):
        inp = inp.split(",")
        if len(inp) != 2:
            idx2 =  self._index
            idx1 =  self._index - 1 if self._index - 1 >= 0 else 0
        else:
            idx2 = int(inp[1])
            idx1 = int(inp[0])
        return self.print_diff_orig(1, idx1, idx2, 8 * 256)

    def print_diff_orig(self, mode, idx1, idx2, rang):
        table1 = self.create_short_table(self.all_frames[idx1]['buf'])
        table2 = self.create_short_table(self.all_frames[idx2]['buf'])
        table3 = self.create_short_table(self.all_frames[idx1]['buf'] + self.all_frames[idx2]['buf'])
        table = " DIFF sets between " + self.all_frames[idx1]['name'] + " and " + self.all_frames[idx2]['name'] + "\n"
        rows = [['BUS', 'ID', 'LENGTH', 'MESSAGE', 'ASCII', 'DESCR', 'COUNT']]
        for fid2, lst2 in table2.items():
            if fid2 not in list(table1.keys()):

                for (lenX, msg, bus, mod), cnt in lst2.items():
                    if self.is_ascii(msg):
                        data_ascii = self.ret_ascii(msg)
                    else:
                        data_ascii = "  "
                    rows.append([str(bus),hex(fid2), str(lenX), self.get_hex(msg), data_ascii, self.get_meta_descr(fid2, msg), str(cnt)])
            elif mode == 0 and len(table3[fid2]) <= rang:
                for (lenX, msg, bus, mod), cnt in lst2.items():

                    if (lenX, msg, bus, mod) not in  table1[fid2]:
                        if self.is_ascii(msg):
                            data_ascii = self.ret_ascii(msg)
                        else:
                            data_ascii = "  "
                        rows.append([str(bus),hex(fid2), str(lenX), self.get_hex(msg), data_ascii, self.get_meta_descr(fid2, msg), str(cnt)])

        cols = list(zip(*rows))
        col_widths = [max(len(value) for value in col) for col in cols]
        format_table = '    '.join(['%%-%ds' % width for width in col_widths ])
        for row in rows:
            table += format_table % tuple(row) + "\n"
        table += "\n"
        return table

    def new_diff(self, def_in, name = ""):
        _name = name.strip()
        _name = _name if _name != "" else "buffer_" + str(len(self.all_frames))
        self._index += 1
        self.all_frames.append({'name':_name,'buf': Replay()})
        self.all_frames[-1]['buf'].add_timestamp()
        return "New buffer  " + _name + ", index: " + str(self._index) + " enabled and active"

    def do_print(self, def_in, index = "-1"):
        _index = int(index)
        temp_buf = Replay()
        if _index == -1:
            for buf in self.all_frames:
                temp_buf = temp_buf + buf['buf']
        else:
            temp_buf = self.all_frames[_index]['buf']

        self._bodyList = self.create_short_table(temp_buf)
        table = "\n"
        rows = [['BUS', 'ID', 'LENGTH', 'MESSAGE', 'ASCII', 'DESCR', 'COUNT']]
        # http://stackoverflow.com/questions/3685195/line-up-columns-of-numbers-print-output-in-table-format
        for fid, lst in self._bodyList.items():
            for (lenX, msg, bus, mod), cnt in lst.items():
                format_ = self.get_meta_bits(fid, lenX)
                if not format_:
                    if self.is_ascii(msg):
                        data_ascii = self.ret_ascii(msg)
                    else:
                        data_ascii = "  "
                    rows.append([str(bus),hex(fid), str(lenX), self.get_hex(msg), data_ascii, self.get_meta_descr(fid, msg), str(cnt)])
                else:
                    idx_0 = 0
                    msg_s = ""
                    for  bitz in format_:
                        fmt = list(bitz.keys())[0]
                        idx = list(list(bitz.values())[0].keys())[0]
                        descr = list(list(bitz.values())[0].values())[0]
                        msg_s += descr + ": " + self.get_data_in_format(msg, idx_0, idx, fmt) + " "
                        idx_0 = idx
                    rows.append([str(bus),hex(fid), str(lenX), msg_s, " ", self.get_meta_descr(fid, msg), str(cnt)])

        cols = list(zip(*rows))
        col_widths = [ max(len(value) for value in col) for col in cols ]
        format_table = '    '.join(['%%-%ds' % width for width in col_widths ])
        for row in rows:
            table += format_table % tuple(row) + "\n"
        table += ""
        return table

    def do_clean(self, def_in):
        self.all_frames = [{'name':'start_buffer','buf':Replay()}]
        self.dump_stat = Replay()
        self._train_buffer = -1
        self._index = 0
        self.data_set = {}
        self._cmdList['act'].is_enabled = False
        self._cmdList['dump_st'].is_enabled = False
        return "Buffers cleaned!"

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if self._need_status and not self._action.is_set():
            self._action.set()
            self._status = self._last/(self._full/100.0)
            self._action.clear()

        if (can_msg.CANData or can_msg.debugData) and not args.get('no_read', False):
            self.all_frames[self._index]['buf'].append(can_msg)

        elif not can_msg.CANData and not can_msg.debugData and not args.get('no_write', False) and not self._action.is_set():
            self._action.set()
            if  self._stat_resend:
                can_msg.CANData = True
                can_msg.CANFrame = copy.deepcopy(self._stat_resend)
                can_msg.bus = self._bus
                self._stat_resend = None
            self._action.clear()

        return can_msg

    def get_data_in_format(self, data, idx_1: int, idx_2: int, format: str):
        #bin_data = ''
        #for byte in data:
        #    bin_data += bin(byte)[2:].zfill(8)
        #print(idx_1)
        #print(idx_2)
        #print(bitstring.BitArray((b'\x00' * (8-len(data))) + data)[idx_1:idx_2])
        selected_value_hex = bitstring.BitArray('0b' + ('0' * ((4 - ( (idx_2-idx_1) %4 ))%4)) + bitstring.BitArray(data)[idx_1:idx_2].bin)
        selected_value_bin = bitstring.BitArray('0b' + bitstring.BitArray(data)[idx_1:idx_2].bin)
        #print((bitstring.BitArray( b'\x00' * (4 - ( (idx_2-idx_1) %4 ))) + bitstring.BitArray( (b'\x00' * (8-len(data))) + data)).bin)
        if format.strip() in ["bin", "b","binary"]:
            return selected_value_bin.bin
        elif format.strip() in ["hex", "h"]:
            return selected_value_hex.hex
        elif format.strip() in ["int","i"]:
            return str(selected_value_hex.int)
        elif format.strip() in ["ascii","a"]:
            return self.ret_ascii(selected_value_bin.bytes)
        else:
            return selected_value_hex.hex

    def show_fields_ecu(self, zd, ecu_id):

        _index = -1
        format = "bin"
        if len(ecu_id.strip().split(",")) == 2:
            format = str(ecu_id.strip().split(",")[1].strip())
        elif len(ecu_id.strip().split(",")) == 3:
            _index = int(ecu_id.strip().split(",")[2])
            format = ecu_id.strip().split(",")[1].strip()


        ecu_id = ecu_id.strip().split(",")[0]

        if ecu_id.strip()[0:2] == '0x':
            ecu_id = int(ecu_id,16)
        else:
            ecu_id = int(ecu_id)



        table = "Data by fields in ECU: " + hex(ecu_id) + "\n\n"
        temp_buf = Replay()

        self.show_fields(0, str(_index))

        if _index == -1:
            for buf in self.all_frames:
                temp_buf = temp_buf + buf['buf']
        else:
            temp_buf = self.all_frames[_index]['buf']

        _bodyList = self.create_short_table(temp_buf)
        list_idx = {}
        for key, value in self.subnet._devices.items():

            if str(key).split(":")[0][0:2] == '0x':
                _ecu_id = int(str(key).split(":")[0], 16)
            else:
                _ecu_id = int(str(key).split(":")[0])
            if _ecu_id == ecu_id:
                list_idx[int(str(key).split(":")[1])] = [value._indexes()]

        if ecu_id in _bodyList:
            for (lenX, msg, bus, mod), cnt in _bodyList[ecu_id].items():
                tmp_f = []
                idx_0 = 0
                for idx in list_idx[lenX][0]:
                    tmp_f.append(self.get_data_in_format(msg, idx_0, idx, format))
                    idx_0 = idx
                list_idx[lenX].append(tmp_f)

        for lenY, msg in list_idx.items():
            table += "\nby length: " + str(lenY) + "\n\n"
            cols = list(zip(*msg[1:]))
            col_widths = [max(len(value) for value in col) for col in cols]
            format_table = '    '.join(['%%-%ds' % width for width in col_widths ])
            for ms in msg[1:]:
                table += format_table % tuple(ms) + "\n"
            table += ""

        return table

    def show_fields(self, zd = 0, _index = "-1"):
        table = ""

        _index = int(_index)
        temp_buf = Replay()
        if _index == -1:
            for buf in self.all_frames:
                temp_buf = temp_buf + buf['buf']
        else:
            temp_buf = self.all_frames[_index]['buf']

        for timestmp, can_msg in temp_buf:
            if can_msg.CANData:
                for _ in self.subnet.process(can_msg.CANFrame):
                        pass
        rows = []
        for key, value in self.subnet._devices.items():
            rows.append(["ECU: " + str(key).split(":")[0], " Length: " + str(key).split(":")[1]," FIELDS DETECTED: " + str(len(value._indexes()))])

        cols = list(zip(*rows))
        col_widths = [max(len(value) for value in col) for col in cols]
        format_table = '    '.join(['%%-%ds' % width for width in col_widths ])
        for row in rows:
            table += format_table % tuple(row) + "\n"
        table += ""

        return table

    def show_change(self, zd = 0, _index = "-1"):
        table = ""
        pars = _index.split(",")
        depth = 31337

        if len(pars) == 2:
            depth = int(pars[1])
            _index = pars[0].strip()

        _index = int(_index)
        temp_buf = Replay()
        if _index == -1:
            for buf in self.all_frames:
                temp_buf = temp_buf + buf['buf']
        else:
            temp_buf = self.all_frames[_index]['buf']

        messages = collections.OrderedDict()

        for timestmp, can_msg in temp_buf:
            if can_msg.CANData:
                if (can_msg.CANFrame.frame_id, can_msg.CANFrame.frame_length) not in messages:
                    messages[(can_msg.CANFrame.frame_id, can_msg.CANFrame.frame_length)] = [[can_msg.CANFrame.frame_raw_data], 0, 1]
                else:
                    messages[(can_msg.CANFrame.frame_id, can_msg.CANFrame.frame_length)][0].append(can_msg.CANFrame.frame_raw_data)
                    if messages[(can_msg.CANFrame.frame_id, can_msg.CANFrame.frame_length)][0][-1] != messages[(can_msg.CANFrame.frame_id, can_msg.CANFrame.frame_length)][0][-2]:
                        messages[(can_msg.CANFrame.frame_id, can_msg.CANFrame.frame_length)][1] += 1
                    if messages[(can_msg.CANFrame.frame_id, can_msg.CANFrame.frame_length)][0][-1] not in messages[(can_msg.CANFrame.frame_id, can_msg.CANFrame.frame_length)][0][:-1]:
                        messages[(can_msg.CANFrame.frame_id, can_msg.CANFrame.frame_length)][2] += 1

        table += "Detected changes (two values):\n\n"
        for (fid, flen), data in messages.items():
            msgs = len(data[0])
            chgs = data[1]
            uniq = data[2]

            if uniq > 1 and msgs > 3 and uniq <= depth:
                table += "\t " + hex(fid) + " count of uniq. values: " + str(uniq) + " values/uniq.: " + str(round(float(msgs/uniq), 2)) + " changes/uniq.: " +(str(round(float(chgs/uniq), 2))) +"\n"

        return table

    def show_detect(self, zd = 0, _index = "0"):
        table = ""

        pars = _index.split(",")
        num_fid = 0

        if len(pars) == 2:
            _index = pars[1].strip()
        else:
            _index = "-1"

        if pars[0].strip().find('0x') == 0:
             num_fid = int(pars[0].split(":")[0], 16)
        else:
             num_fid = int(pars[0].split(":")[0])

        if len(pars[0].split(":")) == 3:
            body = bytes.fromhex(pars[0].split(":")[2].strip())
        else:
            body = bytes.fromhex(pars[0].split(":")[1].strip())

        _index = int(_index)

        temp_buf = Replay()
        if _index == -1:
            for buf in self.all_frames:
                temp_buf = temp_buf + buf['buf']
        else:
            temp_buf = self.all_frames[_index]['buf']

        messages = collections.OrderedDict()
        status = False
        for timestmp, can_msg in temp_buf:
            if can_msg.CANData:
                if can_msg.CANFrame.frame_id == num_fid and can_msg.CANFrame.frame_raw_data == body:
                    status = True
                else:

                    if not status:

                        if can_msg.CANFrame.frame_id not in messages:
                            messages[can_msg.CANFrame.frame_id] = [[can_msg.CANFrame.frame_raw_data], []]
                        else:
                            if can_msg.CANFrame.frame_raw_data not in messages[can_msg.CANFrame.frame_id][0]:
                                messages[can_msg.CANFrame.frame_id][0].append(can_msg.CANFrame.frame_raw_data)

                    else:
                        if can_msg.CANFrame.frame_id not in messages:
                            messages[can_msg.CANFrame.frame_id] = [[], [can_msg.CANFrame.frame_raw_data]]
                        else:
                            if can_msg.CANFrame.frame_raw_data not in messages[can_msg.CANFrame.frame_id][1]:
                                messages[can_msg.CANFrame.frame_id][1].append(can_msg.CANFrame.frame_raw_data)

        table += "Detected changes (by ID " + hex(num_fid) + " ):\n"
        if status:
            for fid, data in messages.items():
                before = data[0]
                after = data[1]
                diff_not = False
                if after != [] and before!= [] and len(before) <= 10 and len(after) <= 10:
                    diff_not = bool([x for x in after if x not in before] != [])
                if diff_not:
                    table += "\n\t ID: " + hex(fid)
                    table += "\n\t\t Changed from: " + "\n"
                    for (st) in [("\t\t" + self.get_hex(x) + "\n") for x in before]:
                         table += st
                    table += "\n\t\t Changed to: " + "\n"
                    for (st) in [("\t\t" + self.get_hex(x) + "\n") for x in after]:
                         table += st

        return table

    def train(self, zn, _index="-1"):
        _index = int(_index.strip())
        temp_buf = Replay()
        if _index == -1:
            for buf in self.all_frames:
                temp_buf = temp_buf + buf['buf']
        else:
            temp_buf = self.all_frames[_index]['buf']

        if self._train_buffer >= 0:
            del self.data_set[self._train_buffer]
        self._train_buffer = _index
        self.data_set.update({_index:{}})

        self._last = 0
        self._full = len(temp_buf)

        if not self._action.is_set():
                    self._action.set()
                    self._need_status = True
                    self._action.clear()
        # Prepare DataSet
        for timestmp, can_msg in temp_buf:
            if can_msg.CANData:
                if can_msg.CANFrame.frame_id not in self.data_set[_index]:

                    self.data_set[_index][can_msg.CANFrame.frame_id] = {

                        'values_array': [ can_msg.CANFrame.get_bits() ],
                        'count': 1,
                        'changes': 0,
                        'last': can_msg.CANFrame.get_bits(),

                        'ch_last_time': round(timestmp,4),
                        'ch_max_time': 0,
                        'ch_min_time': 0,

                        'last_time': round(timestmp,4),
                        'min_time': 0,
                        'max_time': 0,

                        'change_bits': bitstring.BitArray('0b' + ('0' * 64), length=64)

                    }

                else:
                    self.data_set[_index][can_msg.CANFrame.frame_id]['count'] += 1
                    new_arr = can_msg.CANFrame.get_bits()

                    #if  new_arr not in self.data_set[_index][can_msg.CANFrame.frame_id]['values_array']:
                    #    self.data_set[_index][can_msg.CANFrame.frame_id]['values_array'].append(new_arr)

                    if new_arr != self.data_set[_index][can_msg.CANFrame.frame_id]['last']:

                        self.data_set[_index][can_msg.CANFrame.frame_id]['changes'] += 1
                        self.data_set[_index][can_msg.CANFrame.frame_id]['change_bits'] |= (self.data_set[_index][can_msg.CANFrame.frame_id]['last'] ^ new_arr)
                        self.data_set[_index][can_msg.CANFrame.frame_id]['last'] = new_arr

                        if self.data_set[_index][can_msg.CANFrame.frame_id]['changes'] == 2 :
                            self.data_set[_index][can_msg.CANFrame.frame_id]['ch_max_time'] = round(timestmp - self.data_set[_index][can_msg.CANFrame.frame_id]['ch_last_time']+ 0.001,4)
                            self.data_set[_index][can_msg.CANFrame.frame_id]['ch_min_time'] = round(timestmp - self.data_set[_index][can_msg.CANFrame.frame_id]['ch_last_time']- 0.001,4)


                        if self.data_set[_index][can_msg.CANFrame.frame_id]['changes'] > 2:
                            ch_time = round(timestmp - self.data_set[_index][can_msg.CANFrame.frame_id]['ch_last_time'],4)
                            if ch_time > self.data_set[_index][can_msg.CANFrame.frame_id]['ch_max_time']:
                                self.data_set[_index][can_msg.CANFrame.frame_id]['ch_max_time'] = ch_time
                            elif ch_time < self.data_set[_index][can_msg.CANFrame.frame_id]['ch_min_time']:
                                self.data_set[_index][can_msg.CANFrame.frame_id]['ch_min_time'] = ch_time

                        self.data_set[_index][can_msg.CANFrame.frame_id]['ch_last_time'] = round(timestmp,4)


                    if self.data_set[_index][can_msg.CANFrame.frame_id]['count'] == 2:
                         self.data_set[_index][can_msg.CANFrame.frame_id]['max_time'] = round(timestmp - self.data_set[_index][can_msg.CANFrame.frame_id]['last_time']+ 0.001,4)
                         self.data_set[_index][can_msg.CANFrame.frame_id]['min_time'] = round(timestmp - self.data_set[_index][can_msg.CANFrame.frame_id]['last_time']- 0.001,4)

                    if self.data_set[_index][can_msg.CANFrame.frame_id]['count'] > 2:
                        ch_time = round(timestmp - self.data_set[_index][can_msg.CANFrame.frame_id]['last_time'],4)
                        if ch_time > self.data_set[_index][can_msg.CANFrame.frame_id]['max_time']:
                            self.data_set[_index][can_msg.CANFrame.frame_id]['max_time'] = ch_time
                        elif ch_time < self.data_set[_index][can_msg.CANFrame.frame_id]['min_time']:
                            self.data_set[_index][can_msg.CANFrame.frame_id]['min_time'] = ch_time

                    self.data_set[_index][can_msg.CANFrame.frame_id]['last_time'] = round(timestmp,4)

                if not self._action.is_set():
                    self._action.set()
                    self._last += 1
                    self._action.clear()

        time.sleep(1)
        if not self._action.is_set():
                    self._action.set()
                    self._need_status = False
                    self._action.clear()

        return "Profiling finished: " + str(len(self.data_set[_index])) + " uniq. arb. ID"

    def find_ab(self, bred_kakoi_to, _index):
        _index = int(_index.strip())

        if self._train_buffer < 0:
            return "Not trained yet..."
        elif self._train_buffer == _index:
            return "Why?"
        if _index > self._index:
            return "Wrong buffer!"

        temp_buf = self.all_frames[_index]['buf']


        self.data_set.update({_index:{}})

        correlator_changes = []
        known_changes = []
        self.history = []
        self._last = 0
        self._full = len(temp_buf) * 2

        if not self._action.is_set():
                    self._action.set()
                    self._need_status = True
                    self._action.clear()
        # Prepare DataSet
        for timestmp, can_msg in temp_buf:
            if can_msg.CANData:

                if can_msg.CANFrame.frame_id not in self.data_set[_index]:

                    self.data_set[_index][can_msg.CANFrame.frame_id] = {

                        'count': 1,
                        'changes': 0,
                        'last': can_msg.CANFrame.get_bits(),

                        'last_time': round(timestmp,4),


                        'ch_last_time': round(timestmp,4),
                        'diff': bitstring.BitArray('0b'+'0'*64, length=64),
                        'history': [],
                        'curr_comm': 0,
                        'comm': []


                    }

                else:
                    self.data_set[_index][can_msg.CANFrame.frame_id]['count'] += 1
                    new_arr = can_msg.CANFrame.get_bits()

                    chg = self.data_set[_index][can_msg.CANFrame.frame_id].get('changed', False)
                    xchg =  self.data_set[_index][can_msg.CANFrame.frame_id].get('released', False)
                    schg =  self.data_set[_index][can_msg.CANFrame.frame_id].get('changed_same', False)
                    nchg =  self.data_set[_index][can_msg.CANFrame.frame_id].get('changed_1', False)

                    if new_arr != self.data_set[_index][can_msg.CANFrame.frame_id]['last']:

                        self.data_set[_index][can_msg.CANFrame.frame_id]['changes'] += 1
                        diff = new_arr ^ self.data_set[_index][can_msg.CANFrame.frame_id]['last']

                        orig = self.data_set[self._train_buffer].get(can_msg.CANFrame.frame_id, {})
                        orig_bits = orig.get('change_bits', bitstring.BitArray('0b'+'0'*64, length=64))



                        if (diff | orig_bits) != orig_bits:

                            if not chg and not schg and not nchg:
                                self.data_set[_index][can_msg.CANFrame.frame_id]['changed_same'] = False
                                ev = " INITIAL CHANGE (new bitmask), FROM: " + str(self.data_set[_index][can_msg.CANFrame.frame_id]['last'].hex)

                                if len(correlator_changes) > 0:
                                    ev = " " +str([hex(cor) for cor in correlator_changes]) + ev
                                    if can_msg.CANFrame.frame_id not in self.history:
                                        self.history.append(can_msg.CANFrame.frame_id)
                                    self.history = list(set(self.history).union(correlator_changes))
                                    self.data_set[_index][can_msg.CANFrame.frame_id]['comm'].append(" first change from "+ str(self.data_set[_index][can_msg.CANFrame.frame_id]['last'].hex) + ", probably because of next events before: " + str([hex(cor) for cor in correlator_changes]))
                                else:
                                    self.data_set[_index][can_msg.CANFrame.frame_id]['comm'].append(" first event, changed from " + str(self.data_set[_index][can_msg.CANFrame.frame_id]['last'].hex))

                                if  (can_msg.CANFrame.frame_id, self.data_set[_index][can_msg.CANFrame.frame_id]['diff']) not in known_changes:
                                    correlator_changes.append(can_msg.CANFrame.frame_id)


                                self.data_set[_index][can_msg.CANFrame.frame_id].update({'changed': True, 'released': False, 'changed_1': False, 'diff': diff| self.data_set[_index][can_msg.CANFrame.frame_id]['diff']})

                            elif (chg or schg or nchg) and diff == self.data_set[_index][can_msg.CANFrame.frame_id]['diff']  :
                                ev = " RELEASED to original value "
                                self.data_set[_index][can_msg.CANFrame.frame_id]['released'] = True
                                self.data_set[_index][can_msg.CANFrame.frame_id]['changed'] = False
                                self.data_set[_index][can_msg.CANFrame.frame_id]['changed_1'] = False
                                self.data_set[_index][can_msg.CANFrame.frame_id]['changed_same'] = False

                                if can_msg.CANFrame.frame_id in correlator_changes:
                                    correlator_changes.remove(can_msg.CANFrame.frame_id)
                                    known_changes.append((can_msg.CANFrame.frame_id, self.data_set[_index][can_msg.CANFrame.frame_id]['diff']))
                                self.data_set[_index][can_msg.CANFrame.frame_id]['comm'].append(" released value back ")
                            else:
                                ev = " CHANGED AGAIN "

                                if len(correlator_changes) > 0:
                                    ev = " " +str([hex(cor) for cor in correlator_changes]) + ev
                                    if can_msg.CANFrame.frame_id not in self.history:
                                        self.history.append(can_msg.CANFrame.frame_id)
                                    self.history = list(set(self.history).union(correlator_changes))
                                    self.data_set[_index][can_msg.CANFrame.frame_id]['comm'].append(" additional changes, probably because of: " + str([hex(cor) for cor in correlator_changes]))


                                if can_msg.CANFrame.frame_id in correlator_changes:
                                    correlator_changes.remove(can_msg.CANFrame.frame_id)
                                    known_changes.append((can_msg.CANFrame.frame_id, self.data_set[_index][can_msg.CANFrame.frame_id]['diff']))

                                if  (can_msg.CANFrame.frame_id, self.data_set[_index][can_msg.CANFrame.frame_id]['diff']|diff) not in known_changes:
                                    correlator_changes.append(can_msg.CANFrame.frame_id)


                                self.data_set[_index][can_msg.CANFrame.frame_id].update({'diff': (self.data_set[_index][can_msg.CANFrame.frame_id]['diff']|diff)})
                                self.data_set[_index][can_msg.CANFrame.frame_id]['changed_1'] = True
                                self.data_set[_index][can_msg.CANFrame.frame_id]['changed'] = False
                                self.data_set[_index][can_msg.CANFrame.frame_id]['changed_same'] = False
                            msgs = self.data_set[_index][can_msg.CANFrame.frame_id].get('breaking_messages',[])
                            msgs.append("#" + str(self.data_set[_index][can_msg.CANFrame.frame_id]['count'])+" ["+ str(round(timestmp, 4)) +"] " +  can_msg.CANFrame.get_text() + ev ) #+ " diff: " + ( diff | orig_bits).bin + " orig: " + orig_bits.bin + " new: " + diff.bin)
                            self.dump_stat.append_time(timestmp,can_msg)
                            self.data_set[_index][can_msg.CANFrame.frame_id].update({'breaking_messages': msgs})

                    elif self.data_set[_index][can_msg.CANFrame.frame_id].get('changed', False):
                        self.data_set[_index][can_msg.CANFrame.frame_id]['changed'] = False
                        self.data_set[_index][can_msg.CANFrame.frame_id]['changed_same'] = True
                        if can_msg.CANFrame.frame_id in correlator_changes:
                                    correlator_changes.remove(can_msg.CANFrame.frame_id)
                                    known_changes.append((can_msg.CANFrame.frame_id, self.data_set[_index][can_msg.CANFrame.frame_id]['diff']))

                    elif self.data_set[_index][can_msg.CANFrame.frame_id].get('changed_1', False):
                        self.data_set[_index][can_msg.CANFrame.frame_id]['changed_1'] = False
                        self.data_set[_index][can_msg.CANFrame.frame_id]['changed_same'] = True
                        if can_msg.CANFrame.frame_id in correlator_changes:
                                    correlator_changes.remove(can_msg.CANFrame.frame_id)
                                    known_changes.append((can_msg.CANFrame.frame_id, self.data_set[_index][can_msg.CANFrame.frame_id]['diff']))


                    chg = self.data_set[_index][can_msg.CANFrame.frame_id].get('changed', False)
                    xchg =  self.data_set[_index][can_msg.CANFrame.frame_id].get('released', False)
                    schg =  self.data_set[_index][can_msg.CANFrame.frame_id].get('changed_same', False)
                    nchg =  self.data_set[_index][can_msg.CANFrame.frame_id].get('changed_1', False)

                    self.data_set[_index][can_msg.CANFrame.frame_id]['last'] = new_arr
                    self.data_set[_index][can_msg.CANFrame.frame_id]['ch_last_time'] = round(timestmp,4)

                    if self.data_set[_index][can_msg.CANFrame.frame_id]['count'] > 2:
                        orig = self.data_set[self._train_buffer].get(can_msg.CANFrame.frame_id, None)
                        error_rate = 0.04
                        if orig:
                            orig_max_time = orig.get('max_time', None)
                            orig_min_time = orig.get('min_time', None)
                            curr_ch_time = round(timestmp - self.data_set[_index][can_msg.CANFrame.frame_id]['last_time'],4)
                            if orig_max_time is not None and orig_min_time is not None:
                                #error_rate += orig_max_time - orig_min_time
                                if curr_ch_time < (orig_min_time - error_rate):
                                    ev = " 'impulse' rate increased,  delay: " + str(curr_ch_time) + " orig: " + str(orig_min_time)
                                    if schg:
                                        ev = " EVENT CONTINUED " + ev
                                        self.data_set[_index][can_msg.CANFrame.frame_id]['comm'].append(" 'impulse' rate increased abnormally: EVENT")
                                    elif nchg:
                                        ev = " EVENT NEXT STAGE" + ev
                                        self.data_set[_index][can_msg.CANFrame.frame_id]['comm'].append(" 'impulse' rate increased abnormally: NEW STAGE")
                                    elif xchg:
                                        ev = " EVENT FINISHED " + ev
                                        self.data_set[_index][can_msg.CANFrame.frame_id]['comm'].append(" 'impulse' rate increased abnormally: EVENT FINISHED")
                                    elif not chg:
                                        self.data_set[_index][can_msg.CANFrame.frame_id]['comm'].append(" 'impulse' rate increased abnormally...")

                                    if not chg and not nchg  and not xchg:
                                        msgs = self.data_set[_index][can_msg.CANFrame.frame_id].get('breaking_messages',[])
                                        msgs.append("\t#" + str(self.data_set[_index][can_msg.CANFrame.frame_id]['count'])+" ["+ str(round(timestmp, 4)) +"] " + can_msg.CANFrame.get_text() + ev )#)+ " max.time: " + str(orig_max_time) + " min.time: " + str(orig_min_time) + " new time: " + str(curr_ch_time))
                                        self.dump_stat.append_time(timestmp,can_msg)
                                        self.data_set[_index][can_msg.CANFrame.frame_id].update({'breaking_messages': msgs})

                    self.data_set[_index][can_msg.CANFrame.frame_id]['last_time'] = round(timestmp,4)

                if can_msg.CANFrame.frame_id not in self.data_set[self._train_buffer]:
                    correlator_changes.append(can_msg.CANFrame.frame_id)
                    self.data_set[_index][can_msg.CANFrame.frame_id]['comm'].append(" New arb. ID ")
                    msgs = self.data_set[_index][can_msg.CANFrame.frame_id].get('breaking_id_messages',[])
                    msgs.append("#" + str(self.data_set[_index][can_msg.CANFrame.frame_id]['count'])+" ["+ str(round(timestmp, 4)) +"] " + can_msg.CANFrame.get_text() + " NEW Arb. ID")
                    self.dump_stat.append_time(timestmp,can_msg)
                    self.data_set[_index][can_msg.CANFrame.frame_id].update({'breaking_messages': msgs})

                if not self._action.is_set():
                    self._action.set()
                    self._last += 1
                    self._action.clear()

        ### Checking!

        result = " Profiling comparison results (abnormalities by ID):\n\n"

        for aid, body in self.data_set[_index].items():
            # New devices
            msgs = body.get('breaking_messages',[])
            if len(msgs) > 0:
                if aid in self.history:
                    result += "\t" + hex(aid) + " - found abnormalities:\n"
                    for msg  in msgs:
                        result += "\t\t" + msg + "\n"
                else:
                    self.dump_stat.remove_by_id(aid)
            if not self._action.is_set():
                    self._action.set()
                    self._last += body['count']
                    self._action.clear()

        result2 = "\n\nSELECTED SESSION(ready to dump into file now and for ACTIVE check)::\n\n"
        rows = [['TIME', 'ID', 'LENGTH', 'MESSAGE', 'COMMENT']]
        for (tms, can_msg) in self.dump_stat._stream:
            if can_msg.CANData:
                if len(self.data_set[_index][can_msg.CANFrame.frame_id]['comm']) > 0:
                    comment = self.data_set[_index][can_msg.CANFrame.frame_id]['comm'][self.data_set[_index][can_msg.CANFrame.frame_id]['curr_comm']%len(self.data_set[_index][can_msg.CANFrame.frame_id]['comm'])]
                else:
                    comment = " hz "
                self.data_set[_index][can_msg.CANFrame.frame_id]['curr_comm'] += 1
                #result2 += "[" + str(round(tms,4)) + "] " + can_msg.CANFrame.get_text() + " \t\t " + comment + "\n"
                rows.append([str(round(tms,4)), hex(can_msg.CANFrame.frame_id), str(can_msg.CANFrame.frame_length), self.get_hex(can_msg.CANFrame.frame_raw_data), comment ])

        cols = list(zip(*rows))
        col_widths = [ max(len(value) for value in col) for col in cols ]
        format_table = '    '.join(['%%-%ds' % width for width in col_widths ])
        for row in rows:
            result2 += format_table % tuple(row) + "\n"
        result2 += "\n"

        self._rep_index = _index
        self._cmdList['act'].is_enabled = True
        self._cmdList['dump_st'].is_enabled = True

        if not self._action.is_set():
                    self._action.set()
                    self._need_status = False
                    self._action.clear()

        return result2 + result

    def dump_ab(self, fn, file):
        file = file.strip()
        return self.dump_stat.save_dump(file)

    def act_detect(self, fn):
        curr = 0
        weigths = {"Not found": 0}
        self._active_check = True
        if self._active:
            last = len(self.dump_stat)
            if last > 0:
                (last_time, last_frame) = self.dump_stat.get_message(last-1)
                while curr < last - 1:
                    (timeo, test_frame) = self.dump_stat.get_message(curr)
                    waiting_time = last_time - timeo + 1
                    curr += 1
                    if test_frame:
                        key = test_frame.get_text()
                        idg = test_frame.frame_id
                        self.new_diff(0, "STAT_CHECK_ACT_" + key)
                        self.dprint(1, " Sending test frame: " + key)
                        tmp_w = weigths.get(key, 0)
                        #print(1)
                        while self._action.is_set():
                            time.sleep(0.01)
                            #print(2)
                        self._action.set()
                        self._stat_resend = test_frame
                        self._action.clear()
                        #print(3)
                        while 1:
                            time.sleep(1)
                            #print(4)
                            if not self._action.is_set():
                                self._action.set()
                                #print(self._stat_resend)
                                if self._stat_resend is None:
                                    self._action.clear()
                                    self.dprint(1, " Test frame has been sent: " + test_frame.get_text())
                                    time.sleep(waiting_time)
                                    #print(5)
                                    break
                                self._action.clear()
                            #print(6)
                        self.dprint(1, " Check changes... ")
                        self._active = False

                        for idf in  self.history:
                            buf1 = self.all_frames[-1]['buf'].search_messages_by_id(idf)
                            #buf2 = self.dump_stat.search_messages_by_id(idf)

                            buf1x = [bitstring.BitArray( (b'\x00' * (8-len(x))) + x) for x in buf1]

                            j = 0
                            if idf in self.data_set[self._train_buffer]:
                                orig_bits = self.data_set[self._train_buffer][idf]['change_bits']
                            else:
                                orig_bits = bitstring.BitArray( b'\x00' * 8)
                            if idg != idf:
                                looking_bits = orig_bits ^ self.data_set[self._rep_index][idf]['diff']
                                self.dprint(1, "DIFF BIT ("+hex(idf)+"): " + looking_bits.bin)
                                last_b =  orig_bits
                                chg_b = bitstring.BitArray( b'\x00' * 8)
                                itr = 0
                                if len(buf1x) > 1:
                                    for bit in buf1x:
                                        chg_b |= bit ^ last_b
                                        last_b = bit
                                        itr += 1
                                        self.dprint(1, "\nCOMPARE with " + bit.bin + " = " + (looking_bits & chg_b).bin )
                                        if (looking_bits & chg_b).int != 0 and itr > 1:
                                            self.dprint(1, "BINGO")
                                            tmp_w +=1

                        weigths[key] = tmp_w
                        self._active = True
                self.dprint(2, "RET: " + str(weigths))
                self._active_check = False
                max_cur = 0
                return "Event's cause: " + str(max(weigths.keys(), key=(lambda k: weigths[k])))
            else:
                self._active_check = False
                return "stat-check session not found"
        else:
            self._active_check = False
            return "module is not active"


    def load_rep(self, sh, files):
        files = [fl.strip() for fl in files.split(',')]
        ret = "Loaded buffers:\n"
        for fl in files:
            self.new_diff(0, fl + "_buffer")
            self.all_frames[-1]['buf'].parse_file(fl, self._bus)
            ret += "\t"+fl+", index: " + str(len(self.all_frames) - 1) + " with " + str(len(self.all_frames[-1]['buf'].stream) ) + " frames\n"
            self.dprint(0, ret)
        return ret

    def do_start(self, params):

        if len(self.all_frames[-1]['buf'].stream) == 0:
            self.all_frames[-1]['buf'].add_timestamp()
            self.dprint(2, "TIME ADDED")
