modules = {
    'io/hw_USBtin':    {'port':'auto', 'speed':500},  # IO hardware module                           # Module for sniff and replay
    'analyze':    {"bus":'analyze','debug':2},'analyze~2':    {"bus":'analyze'},
    'firewall': {}, 'fuzz':{'debug':2},
    'replay':   {'debug': 1}# Stats
}

# Now let's describe the logic of this test
actions = [
    {'hw_USBtin':   {'action': 'read','pipe': 1}},   # Read to PIPE 1
    {'analyze':    {'pipe': 1}},   # Write generated packets (pings)
    {'firewall': {'white_bus': ["analyze"]}},
    {'replay': {}},
     {'analyze~2':    {'pipe': 1}},
    {'hw_USBtin':   {'action': 'write','pipe': 1}},
    ]
