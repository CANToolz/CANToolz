# Load needed modules
load_modules = {
    'hw_CANBusTriple':    {'port':'auto', 'debug':1, 'speed':500}, # IO hardware module
    'mod_stat' :    {},                                      # Mod stat
    'gen_ping' :    {'debug': 1}                            # Generator/Ping
}
# Now let's describe the logic of this test
actions = [
    {'hw_CANBusTriple':   {'action': 'read','pipe': 2}}, # Read to PIPE 2
    {'mod_stat':    {'pipe': 2}},                  # Statistic for PIPE 2
    {'gen_ping':    {                              # Generate pings to PIPE 1
        'pipe': 1,
        'delay':0.06,
        'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233', # ISO TP data
        'range': [502999, 543002],    # ID range (from 502999 to 543002)
        'mode': 'isotp'} # Send packets in ISO-TP format
    },
    {'hw_CANBusTriple':   {'action': 'write', 'pipe': 1}} # Write generated packets (pings)
    ]

####### let's see how it looks like from the console...
# > python canstoolz.py -c can_ping_discovery.py
#
# hw_USBtin: Init phase started...
# hw_USBtin: Port found: COM14
# hw_USBtin: PORT: COM14
# hw_USBtin: Speed: 500
# hw_USBtin: USBtin device found!
#
#
#    _____          _   _ _______          _
#   / ____|   /\   | \ | |__   __|        | |
#  | |       /  \  |  \| |  | | ___   ___ | |____
#  | |      / /\ \ | . ` |  | |/ _ \ / _ \| |_  /
#  | |____ / ____ \| |\  |  | | (_) | (_) | |/ /
#   \_____/_/    \_\_| \_|  |_|\___/ \___/|_/___|
#
#
#
# >> v
# Loaded queue of modules:
#
# (0)     -       hw_USBtin               {'action': 'read', 'pipe': 2}           Enabled: True
#                 ||
#                 ||
#                 \/
# (1)     -       mod_stat                {'pipe': 2}             Enabled: True
#                 ||
#                 ||
#                 \/
# (2)     -       gen_ping                {'pipe': 1, 'body': '000000000000010203040506070102030405060711121314151617a1a2a3a4a5a6a7112233', 'range': [502999, 543002], 'mode': 'isotp'}
#                 ||
#                 ||
#                 \/
# (3)     -       hw_USBtin               {'action': 'write', 'pipe': 1}          Enabled: True
#
# >>
# >> s                                                     # Start loop
#
# >> c 1 p                                         # print stats of what we have
#
# BUS     LEN     ID              MESSAGE                 COUNT
# 60      8       276             1122334455667788        2
# 60      8       277             1122334455667788        4
# >> c 1 m 0                                   # After a while insert mark and enable alert mode... so then any new foun ID will be printed to output
# >> c 1 p                                     # let's check what we have for now.
#
# BUS     LEN     ID              MESSAGE                 COUNT
# 60      8       276             1122334455667788        128
# 60      8       277             1122334455667788        278
# 60      8       277             1122334455661111        2
# 0       0       0               4d41524b                1     # This is a mark inserted
# >> c 2 s                                               # now start ID bruteforce with
# Active status: True
# New ID found: 510994 (BUS: 60)                                  # here we got new ID
# gen_ping: Loop finished
# >> c 1 p                                     # let's check what we have for now.
#
# BUS     LEN     ID              MESSAGE                 COUNT
# 60      8       276             1122334455667788        230
# 60      8       277             1122334455667788        461
# 60      8       277             1122334455661111        9
# 0       0       0               4d41524b                1     # This is a mark inserted before
# 60      2       510994          01ff                    1     # THIS is detected ID... after mark
