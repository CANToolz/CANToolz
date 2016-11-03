load_modules = {
    'hw_USBtin':    {'port':'auto', 'debug':1, 'speed':500},  # IO hardware module                           # Module for sniff and replay
    'mod_stat':    {}                                         # Stats
}

# Now let's describe the logic of this test
actions = [
    {'hw_USBtin':   {'action': 'read','pipe': 1}},   # Read to PIPE 1
    {'mod_stat':    {'pipe': 1}},   # Write generated packets (pings)
    {'hw_USBtin':   {'action': 'write','pipe': 1}},   # Read to PIPE 1
    ]
