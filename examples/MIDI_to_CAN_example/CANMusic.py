import time
from mido import MidiFile
from mido import MetaMessage
from cantoolz.engine import *
from subprocess import Popen

CANEngine = CANSploit()
CANEngine.load_config("CANToolz_config/BMW_F10_MUSIC.py")
CANEngine.start_loop()
index = CANEngine.find_module('ecu_controls')
time.sleep(1)
#call(["mpg123", "CANToolz_config/track.mp3"]) # File not here, because of COPYRIGHT [ Celldweller – Faction 02]
try:
    prc = Popen("C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe CANToolz_config/track.mp3")
    time.sleep(0.2)
    for message in MidiFile('CANToolz_config/BMW.mid'):
        time.sleep(message.time)
        if not isinstance(message, MetaMessage) and message.type == 'note_on':
            print(str(message.note))
            CANEngine.call_module(index, str(message.note))
except KeyboardInterrupt:
    CANEngine.stop_loop()
    CANEngine.engine_exit()
    print("gg bb")
    exit()
except:
    CANEngine.stop_loop()
    CANEngine.engine_exit()
    print("gg bb")
    exit()
CANEngine.stop_loop()
CANEngine.engine_exit()
