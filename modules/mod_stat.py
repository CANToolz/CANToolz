from libs.module import *
from libs.isotp import *
import collections


class mod_stat(CANModule):
    name = "Service discovery and statistic"

    help = """
    
    This module doing statistic for found CAN messages, putting into STDOUT or file (text/csv).
    Good to see anomalies, behaviour and discovery new IDs
    
    Init parameters: 
    
    [mod_stat]
    file = stats.csv     ; file to save output
    count = 200          ; update file after each <count> messages 
    format = csv         ; format to save, csv or text
       
    """

    _file = None
    _fname = "mod_stat.txt"
    _counter = 0
    _chkCounter = 0
    _bodyList = None
    _logFile = False
    ISOList = None
    _format = 0  # 0 - plain text, 1 - CSV
    _formats = {'CSV': 1, 'text': 0, 'csv': 1, 'txt': 0}
    id = 3
    _active = True
    version = 1.0
    _alert = False

    def doOpenFiles(self):
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

    def doInit(self, params={}):
        self._bodyList = collections.OrderedDict()
        self.ISOList = collections.OrderedDict()
        if 'file' in params:
            self._logFile = True
            self._fname = params['file']

            if 'count' in params:
                self._chkCounter = int(params['count'])
            else:
                self._chkCounter = 100
            if 'format' in params:
                self._format = self._formats[params['format']]

            self._cmdList['f'] = ["Print table to configured file", 0, "", self.cmdFlashFile]
            self.doOpenFiles()

        self._cmdList['p'] = ["Print current table", 0, "", self.stdPrint]
        self._cmdList['c'] = ["Clean table, remove alerts", 0, "", self.cmdClean]
        self._cmdList['m'] = ["Enable alert mode and insert mark into the table", 1, "<ID>", self.addMark]
        self._cmdList['a'] = ["Analyses of captured traffic", 0, "", self.doAnal]
        self._cmdList['i'] = ["Dump ISO to file", 1, " <filename> ", self.doDumpISO]
        self._cmdList['r'] = ["Dump ISO to replay format", 1, " <filename>", self.doDumpReplay]

    def doAnal(self):
        retStr = "ISO TP Messages:\n"
        for id, lst in self._bodyList.iteritems():
            messageISO = ISOTPMessage(id)
            for (lenX, msg, bus, mod), cnt in lst.iteritems():
                ret = messageISO.addCAN(CANMessage.initInt(id, len(msg), [struct.unpack("B", x)[0] for x in msg]))
                if ret < 1:
                    break
                elif messageISO._finished:
                    if id not in self.ISOList:
                        self.ISOList[id] = []
                    self.ISOList[id].append((bus, messageISO._length, messageISO._data))
                    self.dprint(1, "ISO-TP Message detected, with ID " + str(id) + " and length " +
                                str(messageISO._length))
                    retStr += "\tID " + str(id) + " and length " + str(messageISO._length) + "\n"
                    break
        return retStr

    def doDumpReplay(self, name):
        _name = None
        try:
            _name = open(name.strip(), 'w')

            for id, lst in self._bodyList.iteritems():
                for (lenX, msg, bus, mod), cnt in lst.iteritems():
                    _name.write(str(id) + ":" + str(lenX) + ":" + msg.encode('hex') + "\n")
            _name.close()
        except:
            self.dprint(2, "can't open log")

    def doDumpISO(self, name):
        _name = None
        try:
            _name = open(name.strip(), 'w')
        except:
            self.dprint(2, "can't open log")
        if self._format == 0:
            try:
                self.stdISOFile(_name)
            except:
                self.dprint(2, "can't open log")
        elif self._format == 1:
            try:
                self.stdISOFileCSV(_name)
            except:
                self.dprint(2, "can't open log")
        _name.close()
        return ""

    def stdFile(self):
        self._file.seek(0)
        self._file.truncate()
        self._file.write("BUS\tID\tLEN\t\tMESSAGE\t\t\tCOUNT\n")
        self._file.write("")
        for id, lst in self._bodyList.iteritems():
            for (lenX, msg, bus, mod), cnt in lst.iteritems():
                if mod:
                    modx = "\t"
                else:
                    modx = "\t\t"
                sp = " " * (16 - len(msg) * 2)
                self._file.write(str(bus) + "\t" + str(id) + "\t" + str(lenX) + modx + msg.encode('hex') +
                                 sp + '\t' + str(cnt) + "\n")
        return ""

    def stdISOFile(self, _name):

        self._file.seek(0)
        self._file.truncate()
        self._file.write("")
        for id, lst in self.ISOList.iteritems():
            for (bus, length, data) in lst:
                _name.write("\nPacket ID: " + str(id) + "\nBUS:\t" + str(bus) +
                            "\nLength:\t" + str(length) + "\n----------HEX-----------\n" +
                            ''.join(struct.pack("!B", b) for b in data).encode('hex') +
                            '\n----------ASCII--------------\n' +
                            ''.join(struct.pack("!B", b) for b in data) + '\n----------------------\n\n')
        return ""

    def stdISOFileCSV(self, _name):

        self._file.seek(0)
        self._file.truncate()
        self._file.write("BUS,ID,LENGTH,MESSAGE,ASCII\n")
        self._file.write("")
        for id, lst in self.ISOList.iteritems():
            for (bus, length, data) in lst:
                _name.write(str(bus) + "," + str(id) +
                            "," + str(length) + "," + ''.join(struct.pack("!B", b) for b in data).encode('hex') +
                            "," + ''.join(struct.pack("!B", b) for b in data) + "\n")
        return ""

    def stdFileCSV(self):
        self._file.seek(0)
        self._file.truncate()
        self._file.write("BUS,ID,LENGTH,MESSAGE,COUNT\n")
        for id, lst in self._bodyList.iteritems():
            for (len, msg, bus, mod), cnt in lst.iteritems():
                self._file.write(str(bus) + "," + str(id) + "," + str(len) + "," + msg.encode('hex') +
                                 ',' + str(cnt) + "\n")
        return ""

    def stdPrint(self):
        table = "\n"
        table += "BUS\tID\tLENGTH\t\tMESSAGE\t\t\tCOUNT"
        table += "\n"
        for id, lst in self._bodyList.iteritems():
            for (lenX, msg, bus, mod), cnt in lst.iteritems():
                if mod:
                    modx = "\t"
                else:
                    modx = "\t\t"
                sp = " " * (16 - len(msg) * 2)
                table += str(bus) + "\t" + str(id) + "\t" + str(lenX) + modx + msg.encode('hex') + sp + '\t' + str(
                    cnt) + "\n"
        table += ""
        return table

    def addMark(self, x):
        self._bodyList[int(x)] = collections.OrderedDict()
        self._bodyList[int(x)][(0, "MARK", 0, False)] = 1
        self._alert = True
        return ""

    def cmdFlashFile(self):
        if self._format == 0:
            try:
                self.stdFile()
            except:
                self.dprint(2, "can't open log")

        elif self._format == 1:
            try:
                self.stdFileCSV()
            except:
                self.dprint(2, "can't open log")
        return ""

    def cmdClean(self):
        self._bodyList = collections.OrderedDict()
        self._alert = False
        self.ISOList = collections.OrderedDict()
        return ""

        # Effect (could be fuzz operation, sniff, filter or whatever)

    def doEffect(self, CANMsg, args={}):
        if CANMsg.CANData:
            if CANMsg.CANFrame._id not in self._bodyList:
                self._bodyList[CANMsg.CANFrame._id] = collections.OrderedDict()
                self._bodyList[CANMsg.CANFrame._id][(
                    CANMsg.CANFrame._length,
                    CANMsg.CANFrame._rawData,
                    CANMsg._bus,
                    CANMsg.CANFrame._ext)
                ] = 1
                if self._alert:
                    print "New ID found: " + str(CANMsg.CANFrame._id) + " (BUS: " + str(CANMsg._bus) + ")"
            else:
                if (CANMsg.CANFrame._length,
                    CANMsg.CANFrame._rawData,
                    CANMsg._bus,
                    CANMsg.CANFrame._ext) not in self._bodyList[CANMsg.CANFrame._id]:
                    self._bodyList[CANMsg.CANFrame._id][(
                        CANMsg.CANFrame._length,
                        CANMsg.CANFrame._rawData,
                        CANMsg._bus,
                        CANMsg.CANFrame._ext)
                    ] = 1
                else:
                    self._bodyList[CANMsg.CANFrame._id][(
                        CANMsg.CANFrame._length,
                        CANMsg.CANFrame._rawData,
                        CANMsg._bus,
                        CANMsg.CANFrame._ext)
                    ] += 1

            if self._logFile:
                self._counter += 1
                if self._counter >= self._chkCounter:
                    self._counter = 0
                    self.cmdFlashFile()

        return CANMsg
