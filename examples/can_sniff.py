modules = {
    'io/hw_USBtin':    {'port':'auto', 'debug':1, 'speed':500},  # IO hardware module                           # Module for sniff and replay
    'analyze':    {}                                         # Stats
}

# Now let's describe the logic of this test
actions = [
    {'hw_USBtin':   {'action': 'read','pipe': 1}},   # Read to PIPE 1
    {'analyze':    {'pipe': 1}}   # Write generated packets (pings)
    ]
