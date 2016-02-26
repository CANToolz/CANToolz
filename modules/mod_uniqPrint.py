from libs.module import *
from libs.can import *
import collections


class mod_uniqPrint(CANModule):
    name="Service discovery and statistic"
    
    help="""
    
    This module doing statistic for found CAN messages, putting into STDOUT or file (text/csv).
    Good to see anomalies, behaviour and discovery new IDs
    
    Init parameters: 
    
    [mod_uniqPrint]
    file = stats.csv     ; file to save output
    count = 200          ; update file after each <count> messages 
    format = csv         ; format to save, csv or text
    
    Module parameters: 
       mark - enable alerting after X packets
         {'mark':200} // NOT SUPPORTED YET!!! Manual Marking only now
    
    Console interrupts:
       p   -   print current table
       c   -   clena current table
       f   -   print as plain to file 
       t   -   print as CSV to file 
       s   -   start/stop collecting stats
       m <x>  -   put mark as id X into the table
       Example (console input): c 3 p
       
    """
    
    _file=None
    _fname=None
    _counter=0
    _chkCounter=0
    _bodyList=None
    _logFile=False
    _format=0 # 0 - plain text, 1 - CSV
    _formats={'CSV':1,'text':0,'csv':1,'txt':0}
    id=3
    _logging=True
    version=1.0
    _alert=False
    def doStart(self):
        try:
            self._file = open(self._fname, 'w')
        except:
            self.dprint(2,"can't open log")
            
    def doStop(self):
        try:
            self._file.close()
        except:
            self.dprint(2,"can't open log")
            
    def doInit(self,params={}):
        self._bodyList=collections.OrderedDict()
        if 'file' in params:
            self._logFile=True
            self._fname=params['file']
            
            if 'count' in params:
                self._chkCounter=int(params['count'])
            else:
                self._chkCounter=100
            if 'format' in params: 
                self._format=self._formats[params['format']]
                
    def stdFile(self):  
    
        self._file.seek(0)
        self._file.truncate()
        self._file.write("BUS\tLEN\tID\t\tMESSAGE\t\t\tCOUNT\n")
        self._file.write("")
        for id,lst in self._bodyList.iteritems():
            for (len,msg,bus,mod),cnt in lst.iteritems():
                if mod:
                    modx="\t"
                else:
                    modx="\t\t"
                self._file.write(str(bus)+"\t"+str(len)+"\t"+str(id)+modx+msg.encode('hex')+'\t'+str(cnt)+"\n")
                
    def stdFileCSV(self):  
    
        self._file.seek(0)
        self._file.truncate()
        self._file.write("BUS,LENGTH,ID,MESSAGE,COUNT\n")
        for id,lst in self._bodyList.iteritems():
            for (len,msg,bus,mod),cnt in lst.iteritems():
                self._file.write(str(bus)+","+str(len)+","+str(id)+","+msg.encode('hex')+','+str(cnt)+"\n")
                               
    def stdPrint(self):  
        print
        print
        print "BUS\tLEN\tID\t\tMESSAGE\t\t\tCOUNT"
        print
            
        for id,lst in self._bodyList.iteritems():
            for (len,msg,bus,mod),cnt in lst.iteritems():
                if mod:
                    modx="\t"
                else:
                    modx="\t\t"
                    
                print str(bus)+"\t"+str(len)+"\t"+str(id)+modx+msg.encode('hex')+'\t'+str(cnt)+"\n"
        print
        print
    
    def addMark(self, x):
        self._bodyList[x] = collections.OrderedDict()
        self._bodyList[x][(0,"MARK",0,False)]=1
        self._alert=True
    def rawWrite(self,data):
        if data=="p": #print table to stdout
            self.stdPrint()
        elif data[0]=="m": #print table to stdout
            try:
                x=int(data[1:])
            except:
                x=0
            self.addMark(x)    
        elif data == "s":
            if self._logging:
                self._logging=False
            else:
                self._logging=True
        elif data=="f": #print table to stdout
            if self._format==0:
                self.stdFile()
            elif self._format==1:
                self.stdFileCSV()   
                
        elif data=="c": #clean table
            self._bodyList=collections.OrderedDict()
            self._alert=False
        
    # Effect (could be fuzz operation, sniff, filter or whatever)
    def doEffect(self, CANMsg,args={}):
        if CANMsg.CANData and self._logging:
            if CANMsg.CANFrame._id not in self._bodyList:
                self._bodyList[CANMsg.CANFrame._id] = collections.OrderedDict()
                self._bodyList[CANMsg.CANFrame._id][(CANMsg.CANFrame._length,CANMsg.CANFrame._rawData,CANMsg._bus,CANMsg.CANFrame._ext)]=1
                if self._alert:
                    print "New ID found: "+str(CANMsg.CANFrame._id)+" (BUS:"+str(CANMsg._bus)+")"
            else:
                if (CANMsg.CANFrame._length,CANMsg.CANFrame._rawData,CANMsg._bus,CANMsg.CANFrame._ext) not in self._bodyList[CANMsg.CANFrame._id]:
                    self._bodyList[CANMsg.CANFrame._id][(CANMsg.CANFrame._length,CANMsg.CANFrame._rawData,CANMsg._bus,CANMsg.CANFrame._ext)]=1
                else:
                    self._bodyList[CANMsg.CANFrame._id][(CANMsg.CANFrame._length,CANMsg.CANFrame._rawData,CANMsg._bus,CANMsg.CANFrame._ext)]+=1
        
            if self._logFile:
                self._counter+=1
                if self._counter>=self._chkCounter:
                    self._counter=0
                    if self._format==0:
                        self.stdFile()   # Lof to file stats
                    if self._format==1:    
                        self.stdFileCSV() 
                        
        return CANMsg


        
