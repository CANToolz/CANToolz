load_modules = {
    'hw_USBtin':    {'port':'auto', 'debug':1, 'speed':125},  # IO hardware module                           # Module for sniff and replay
    'mod_stat':    {},
    'mod_firewall': {},
    'gen_replay':   {'debug': 1}# Stats
}

# Now let's describe the logic of this test
actions = [
    {'hw_USBtin':   {'action': 'read','pipe': 1}},   # Read to PIPE 1
    {'mod_firewall': {'black_list': [251159376]}},
    {'mod_stat':    {'pipe': 1}},   # Write generated packets (pings)
    {'gen_replay':   {'pipe': 2, 'delay':0.06}},
    {'hw_USBtin':   {'action': 'write','pipe': 2}},
    ]
