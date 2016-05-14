import time
from mido import MidiFile
from mido import MetaMessage
from cantoolz.engine import *

CANEngine = CANSploit()
CANEngine.load_config("CANToolz_config/BMW_E90_MUSIC.py")
CANEngine.start_loop()
index = CANEngine.find_module('ecu_controls')

for message in MidiFile('CANToolz_config/BMW.mid'):
	time.sleep(message.time)
	if not isinstance(message, MetaMessage) and message.type == 'note_on':
		CANEngine.call_module(index, str(message.note))
