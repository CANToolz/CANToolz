import time
from mido import MidiFile
from mido import MetaMessage
from cantoolz.engine import *
from subprocess import call

CANEngine = CANSploit()
CANEngine.load_config("CANToolz_config/BMW_F10_MUSIC.py")
CANEngine.start_loop()
index = CANEngine.find_module('ecu_controls')

call(["mpg123", "CANToolz_config/track.mp3"]) # File not here, because of COPYRIGHT [ Celldweller – Faction 02]
time.sleep(0.2)

for message in MidiFile('CANToolz_config/BMW.mid'):
    time.sleep(message.time)
    if not isinstance(message, MetaMessage) and message.type == 'note_on':
        CANEngine.call_module(index, str(message.note))

CANEngine.stop_loop()
CANEngine.exit()
