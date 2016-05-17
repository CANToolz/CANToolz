import time
from mido import MidiFile
from mido import MetaMessage
from cantoolz.engine import *
from subprocess import Popen

CANEngine = CANSploit()
CANEngine.load_config("CANToolz_config/BMW_F10_MUSIC.py")
CANEngine.start_loop()
index = CANEngine.find_module('ecu_controls')
index2 = CANEngine.find_module('mod_stat')
while not CANEngine.status_loop:
    time.sleep(0.000001)

try:
    # CHANGE PATH TO PLAYER AND TRACK HERE!!!!!!
    prc = Popen("C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe CANToolz_config/track.mp3")
    time.sleep(0.2)
    for message in MidiFile('CANToolz_config/BMW.mid'):
        time.sleep(message.time)
        if not isinstance(message, MetaMessage) and message.type == 'note_on':
            print(str(message.note))
            CANEngine.call_module(index, str(message.note))
        print(CANEngine.call_module(index2, "p"))
except KeyboardInterrupt:
    print("gg bb, do not press ctrl-c again!")
except:
    print("gg hf")

CANEngine.stop_loop()
CANEngine.engine_exit()

while CANEngine.status_loop:
    time.sleep(0.000001)
