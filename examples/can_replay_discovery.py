# Load needed modules
load_modules = {
    'hw_USBtin':    {'port':'auto', 'debug':1, 'speed':500,'bus':'1'},  # IO hardware module
    'hw_USBtin~2':    {'port':'auto', 'debug':1, 'speed':500,'bus':'2'},  # IO hardware module
    'gen_replay':   {'debug': 1,'bus':'old'},
    'gen_replay~2':   {'debug': 1,'bus':'new'},# Module for sniff and replay
    'mod_firewall':{}, 'mod_stat~2':    {},
    'mod_stat':    {}                                         # Stats
}

# Now let's describe the logic of this test
actions = [
    {'hw_USBtin':   {'action': 'read','pipe': 1}},  {'gen_replay~2':    {'pipe': 1, 'delay':0.01}}, # Read to PIPE 1
    {'mod_stat':{}}, {'mod_firewall':{'white_bus':'new'}},{'hw_USBtin':   {'action': 'write','pipe': 1}},
        # Dump DIFF replay or replay from PIPE 1
    {'gen_replay':    {'pipe': 2, 'delay':0.01}},
    {'mod_stat~2':{'pipe':2}},
    {'mod_firewall':{'white_bus':'old','pipe':2}},# Load dumped and then replay to PIPE 2
    {'hw_USBtin~2':    {'action':'write','pipe': 2}}   # Write generated packets (pings)
    ]

