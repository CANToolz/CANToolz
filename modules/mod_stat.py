from libs.module import *
from libs.can import *
import collections


class mod_stat(CANModule):
    name="Service discovery and statistic"
    
    help="""
    
    This module doing statistic for found CAN messages, putting into STDOUT or file (text/csv).
    Good to see anomalies, behaviour and discovery new IDs
    
    Init parameters: 
    
    [mod_stat]
    file = stats.csv     ; file to save output
    count = 200          ; update file after each <count> messages 
    format = csv         ; format to save, csv or text
       
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
    _active=True
    version=1.0
    _alert=False
    def doStart(self):
        if self._logFile:
            try:
                self._file = open(self._fname, 'w')
            except:
                self.dprint(2,"can't open log")
                
    def doStop(self):
        if self._logFile:
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
                
            self._cmdList['f']=["Print table to configured file",0,"",self.cmdFlashFile] 
            
        self._cmdList['p']=["Print current table",0,"",self.stdPrint]
        self._cmdList['c']=["Clean table, remove alerts",0,"",self.cmdFlashFile]
        self._cmdList['m']=["Enable alert mode and insert mark into the table",1,"<ID>",self.addMark]   
            
                
    def stdFile(self):  
    
        self._file.seek(0)
        self._file.truncate()
        self._file.write("BUS\tLEN\tID\t\tMESSAGE\t\t\tCOUNT\n")
        self._file.write("")
        for id,lst in self._bodyList.iteritems():
            for (lenX,msg,bus,mod),cnt in lst.iteritems():
                if mod:
                    modx="\t"
                else:
                    modx="\t\t"
                sp=" "*(16-len(msg)*2)       
                self._file.write(str(bus)+"\t"+str(lenX)+"\t"+str(id)+modx+msg.encode('hex')+sp+'\t'+str(cnt)+"\n")
        return ""          
                
    def stdFileCSV(self):  
        self._file.seek(0)
        self._file.truncate()
        self._file.write("BUS,LENGTH,ID,MESSAGE,COUNT\n")
        for id,lst in self._bodyList.iteritems():
            for (len,msg,bus,mod),cnt in lst.iteritems():
                self._file.write(str(bus)+","+str(len)+","+str(id)+","+msg.encode('hex')+','+str(cnt)+"\n")
        return ""    
        
    def stdPrint(self):  
        table = "\n"
        table += "BUS\tLEN\tID\t\tMESSAGE\t\t\tCOUNT"
        table += "\n"    
        for id,lst in self._bodyList.iteritems():
            for (lenX,msg,bus,mod),cnt in lst.iteritems():
                if mod:
                    modx="\t"
                else:
                    modx="\t\t"
                sp=" "*(16-len(msg)*2)   
                table += str(bus)+"\t"+str(lenX)+"\t"+str(id)+modx+msg.encode('hex')+sp+'\t'+str(cnt)+"\n"
        table+=""
        return table
    
    def addMark(self, x):
        self._bodyList[int(x)] = collections.OrderedDict()
        self._bodyList[int(x)][(0,"MARK",0,False)]=1
        self._alert=True
        return ""  
        
    def cmdFlashFile(self):
        if self._format==0:
            self.stdFile()
        elif self._format==1:
            self.stdFileCSV()   
        return ""    
        
    def cmdFlashFile(self):
        self._bodyList=collections.OrderedDict()
        self._alert=False
        return ""  
        
    # Effect (could be fuzz operation, sniff, filter or whatever)
    def doEffect(self, CANMsg,args={}):
        if CANMsg.CANData:
            if CANMsg.CANFrame._id not in self._bodyList:
                self._bodyList[CANMsg.CANFrame._id] = collections.OrderedDict()
                self._bodyList[CANMsg.CANFrame._id][(CANMsg.CANFrame._length,CANMsg.CANFrame._rawData,CANMsg._bus,CANMsg.CANFrame._ext)]=1
                if self._alert:
                    print "New ID found: "+str(CANMsg.CANFrame._id)+" (BUS: "+str(CANMsg._bus)+")"
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


        
