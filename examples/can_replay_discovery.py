# Load needed modules
load_modules = {
    'hw_USBtin':    {'port':'auto', 'debug':1, 'speed':500},  # IO hardware module
    'gen_replay':   {'debug': 1},                             # Module for sniff and replay
    'mod_stat':    {}                                         # Stats
}

# Now let's describe the logic of this test
actions = [
    {'hw_USBtin':   {'action': 'read','pipe': 1}},   # Read to PIPE 1
    {'mod_stat':{}},                                 # Dump DIFF replay or replay from PIPE 1
    {'gen_replay':    {'pipe': 2}},    # Load dumped and then replay to PIPE 2
    {'hw_USBtin':    {'action':'write','pipe': 2}}   # Write generated packets (pings)
    ]

