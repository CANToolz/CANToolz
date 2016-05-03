load_modules = {
    'hw_USBtin':    {'port':'loop', 'debug':1, 'speed':500},  # IO hardware module

    'gen_ping':   {'debug': 1},
    'gen_replay'   : {'load_from': 'tests/test_responses2.save'}, # Module for sniff and replay
    'mod_stat':    {}                                         # Stats
}

# Now let's describe the logic of this test
actions = [
    {'hw_USBtin':   {'action': 'read','pipe': 1}},   # Read to PIPE 1
    {'gen_ping'       : {
        'pipe':2,
        'range': [1790, 1810],
        'services':[
            {'service':0x01, 'sub':0x0d},
            {'service':0x09, 'sub':0x02},
            {'service':0x2F, 'sub':0x03,
             'data':[7,3,0,0]}],
        'mode':'UDS','padding':0x41}
    },{'gen_replay'     : {'pipe':2}},
    {'mod_stat':{}},# We will sniff first from PIPE 1, then replay to PIPE 2
    {'hw_USBtin':    {'action':'write','pipe': 2}}   # Write generated packets (pings)
    ]