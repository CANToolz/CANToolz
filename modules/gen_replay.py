from libs.module import *
from libs.can import *


class gen_replay(CANModule):
    name="Replay module"
    
    help="""
    
    This module doing replay of captured packets. 
    
    Init parameters: none
        load_from  - load packets from file (optional)
        save_to  - save to file (mod_replay.save by default)
              
    """
    
    _file=None
    _fname=None

    CANList=[]

    _active=True
    version=1.0

    _replay=False
    _sniff=False
    
    
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
        if 'save_to' in params:
            self._fname=params['save_to']
        else:
            self._fname="mod_replay.save"
        
        if 'load_from' in params:
            try:
                with open(params['load_from'], "r") as ins:
                    for line in ins:
                        id=line[:-1].split(":")[0]
                        length=line[:-1].split(":")[1]
                        data=line[:-1].split(":")[2]
                        self.CANList.append(CANMessage.initInt(int(id),int(length),[struct.unpack("B",x)[0] for x in data.decode('hex')[:8]]))
                self.dprint(1,"Loaded "+str(len(self.CANList))+" frames")        
            except:
                self.dprint(2,"can't open files with CAN messages!")
                
     
        self._cmdList['p']=["Print count of loaded packets",0,"",self.cntPrint]
        self._cmdList['r']=["Replay range from loaded, from number X to number Y",1," <X>-<Y> ",self.replayMode]
        self._cmdList['d']=["Save range of loaded packets, from X to Y",1," <X>-<Y> (if no parameters then all)",self.saveDump]
        self._cmdList['c']=["Clean loaded table",0,"",self.clnTable]   
        self._cmdList['g']=["Enable/Disable sniff mode to collect packets",0,"",self.sniffMode] 
        
    def clnTable(self):
        self.CANList=[]
        return ""
        
    def saveDump(self, indexes):
        ret="Saved to "+self._fname
        _num1=0
        _num2=len(self.CANList)
        try:
            _num1=int(idexes.split("-")[0])
            _num2=int(idexes.split("-")[1])
        except:
            _num1=0
            _num2=len(self.CANList)
        if _num2>_num1 and _num1<=len(self.CANList)and _num2<=len(self.CANList) and _num1>=0 and _num2>0:
            try:
                for i in range(_num1,_num2):
                    self._file.write(str(self.CANList[i]._id)+":"+str(self.CANList[i]._length)+":"+str(self.CANList[i]._rawData.encode('hex'))+"\n")
            except Exception as e:
                ret="Not saved. Error: "+str(e)
        return ret
        
    def sniffMode(self):
        self._replay=False
        if self._sniff:
            self._sniff=False
        else:
            self._sniff=True   
        return str(self._sniff)

    def replayMode(self,idexes):
        self._replay=False
        self._sniff=False
        try:
            self._num1=int(idexes.split("-")[0])
            self._num2=int(idexes.split("-")[1])
            if self._num2>self._num1 and self._num1<len(self.CANList)and self._num2<=len(self.CANList) and self._num1>=0 and self._num2>0:
                self._replay=True
        except:
                self._replay=False
                
        return str(self._replay)        
        
    def cntPrint(self):
        ret = str(len(self.CANList))
        return ret
     
    # Effect (could be fuzz operation, sniff, filter or whatever)
    def doEffect(self, CANMsg,args={}):
        if self._sniff and CANMsg.CANData:
            self.CANList.append(CANMsg.CANFrame)
        elif self._replay:
            CANMsg.CANFrame=self.CANList[self._num1]
            self._num1+=1
            CANMsg.CANData=True
            if self._num1==self._num2:
                self._replay=False
                               
        return CANMsg


        
