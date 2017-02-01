load_modules = {
    'hw_USBtin':    {'port':'auto', 'speed':500},  # IO hardware module                           # Module for sniff and replay
    'mod_stat':    {"bus":'mod_stat','debug':2},'mod_stat~2':    {"bus":'mod_stat'},
    'mod_firewall': {}, 'mod_fuzz1':{'debug':2},
    'gen_replay':   {'debug': 1}# Stats
}

# Now let's describe the logic of this test
actions = [
    {'hw_USBtin':   {'action': 'read','pipe': 1}},   # Read to PIPE 1
    {'mod_stat':    {'pipe': 1}},   # Write generated packets (pings)
    {'mod_firewall': {'white_bus': ["mod_stat"]}},
    {'gen_replay': {}},
     {'mod_stat~2':    {'pipe': 1}},
    {'hw_USBtin':   {'action': 'write','pipe': 1}},
    ]
