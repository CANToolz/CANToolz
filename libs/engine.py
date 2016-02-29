from libs.can import *
from libs.module import *

import sys
import glob, os
import threading
import re
import struct
import signal
import ConfigParser
import ast

import time

'''
Main class
'''  

class CANSploit:

  
    DEBUG = 0

    
    def dprint(self,level,msg):
        if level<= self.DEBUG:
            print self.__class__.__name__+": "+msg  
            
    def __init__(self):
        self._version = "0.9b"           # version
        self._enabledList=[]             # queue of active modules with params
        self._pipes   = [None,None]      # two pipes with CANMessages
        self._type = {}                  # Pointers on instances here
        self._modules =[]                # loaded modules 
        self._thread=None
        self._mainThread=None
        self._stop = threading.Event() 
        self._raw = threading.Event()
        self._idc=-1
        sys.path.append('./modules') 
        sys.dont_write_bytecode=True
        
    # Main loop with two pipes
    def mainLoop(self):
        #Run until STOP
        while (not self._stop.is_set()):               
            self._pipes[0]=CANSploitMessage() # Prepare empty message
            self._pipes[1]=CANSploitMessage() # Prepare empty message
            for  name,module,params,pipe in self._enabledList: # Each module
                #  Handle CAN message
                if module._active:
                    module._block.wait(3)
                    module._block.clear()    
                    self._pipes[pipe]=module.doEffect(self._pipes[pipe],params)   # doEffect on CANMessage 
                    module._block.set() 
            
        #Here when STOP            
        for name,module,params,pipe in self._enabledList:
            module.doStop()
            
    # Call module command        
    def callModule(self, mod,params): 
        x=self.findModule(mod)
        if x>=0:
            ret = self._enabledList[x][1].rawWrite(params)
        else:
            ret = "Module "+mod+" not loaded!"
        return ret
        
    # Enable loop        
    def startLoop(self):
        self._stop.clear()

        
        for name,module,params,pipe in self._enabledList:
            module.doStart()
            module._block.set()
                    
        self._thread = threading.Thread(target=self.mainLoop)
                
        self._thread.daemon = True
        self._thread.start()
        
    # Pause loop      
    def stopLoop(self):
        self._stop.set()
    
    # Having defulat values for id and pipe params    
    def checkParams(self,mod, params):
        if 'pipe' in params:
            pipe= 1 if int(params['pipe'])>2 else int(params['pipe'])-1
        else:
            params['pipe']=1
            pipe=0
        
        #if 'enabled' not in params:
        #    params['enabled']=True
            
        return [params,  pipe]
    
    # Add module and params to the end    
    def pushModule(self,mod,params):
    
        chkdParams=self.checkParams(mod,params)
            
        self._enabledList.append([mod,self._type[mod.split("!")[0]],chkdParams[0],chkdParams[1]])
        
    # Find index of module with name mod    
    def findModule(self,mod):
        i=0
        x=-1
        for  name,module,params,pipe in self._enabledList:
            if name==mod:
                x=i
                break;
            i+=1  
        return x        
    
    # Add new params to module named mod    
    def editModule(self, mod,params):
        x=self.findModule(mod)
        if x>=0:
            chkdParams=self.checkParams(mod,params)
            self._enabledList[x][2]=chkdParams[0]
            self._enabledList[x][3]=chkdParams[1]
            return x
        return -1
    
    # Edit value of parameters of module mod    
    def editModuleParam(self, mod,key,value):
        x=self.findModule(mod)
        if x>=0:
            self._enabledList[x][2][key]=value
            return x
        return -1
    
    # Get value of parameter    
    def getModuleParams(self, mod,key):
        x=self.findModule(mod)
        if x>=0:
            return self._enabledList[x][2][key]
        return None
    
    # Get all modules and parameters    
    def getModulesList(self):
        return self._enabledList
    
    # Get all parameters for module named mod    
    def getModuleParams(self, mod):
        x=self.findModule(mod)
        if x>=0:
            return self._enabledList[x][2]
        return None 
    
    # Load and init new module form lib    
    def initModule(self,mod,params):    
                    
        self._modules.append(__import__(mod.split("~")[0]))
        exec('cls=self._modules[-1].'+mod.split("~")[0]+'(params)') # init module
        self._type[mod]=cls 
    
    # Load all modules and params form config file    
    def loadConfig(self,path): # Load config from file
        config = ConfigParser.ConfigParser()
        config.optionxform = str
        
        #if 1==1:
        try:        
            config.read([path])
            sects=config.sections()
          
            for mod_name in sects:
                
                if mod_name=="MITM":             # Load effects order
                    paramz_=config.items('MITM')
                    
                    for (mod,settings) in paramz_:
                        paramz=ast.literal_eval(settings)
                        self.pushModule(mod,paramz)    
                        #self._enabledList[mod]=[self._type[_mod],paramz]
                     
                else:                           # Load modules
                    cls=None
                    paramz_=config.items(mod_name)
                    paramz=dict((y, x) for y, x in paramz_)
                    self.initModule(mod_name,paramz)
    
        except Exception as e:
            self._enabledList=[]
            self._modules=[]
            self.dprint(0,"Can't parse config: "+str(e))
            return -1
            
        return 1
            


    
            
        
        