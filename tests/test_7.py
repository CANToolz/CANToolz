load_modules = {
    'hw_USBtin':    {'port':'loop', 'debug':1, 'speed':500},  # IO hardware module

    'gen_replay':   {'debug': 1, 'load_from': 'tests/test_responses.save'},                             # Module for sniff and replay
    'mod_stat':    {}                                         # Stats
}

# Now let's describe the logic of this test
actions = [
    {'hw_USBtin':   {'action': 'read','pipe': 1}},   # Read to PIPE 1
    {'gen_replay':    {'pipe': 2}},
    {'mod_stat':{}},# We will sniff first from PIPE 1, then replay to PIPE 2
    {'hw_USBtin':    {'action':'write','pipe': 2}}   # Write generated packets (pings)
    ]