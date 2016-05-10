# Examples from:
#        "CarHackersHandbook" by Craig Smith (UDS scan) (page 55)
#        "Adventures	in	Automotive	Networks and Control Units" by  Charlie Miller and Chris Valasek
#

# Load needed modules
load_modules = {
    'hw_USBtin':    {'port': 'auto', 'debug': 1, 'speed': 500},                # IO hardware module
    'gen_ping' :    {},                                                     # Generator/Ping
    'mod_stat':     {}                                                      # Mod stat to see results
}

actions = [
    {'hw_USBtin':   {'action': 'read'}}, # Read to PIPE 1
    {'mod_stat':    {}},                 # Mod stat (with CAN traffic analyzer)
    {'gen_ping':    {                    # Generate UDS requests
        'pipe': 2,
        'delay': 0.06,
        'range': [1, 2047],           # ID range (from 1790 to 1794)
        'services':[{'service': 0x10, 'sub': 0x01},
                    {'service': 0x3E, 'sub': 0x01}],
        'mode':'UDS'}
    },
    {'mod_stat':    {'pipe': 2}},
     {'hw_USBtin':   {'action': 'write','pipe':2}}
    ]


