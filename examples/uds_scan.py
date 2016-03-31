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
        'range': [1, 2047],           # ID range (from 1790 to 1794)
        'services':[{'service': 0x01, 'sub': 0x0d}, # Service mode and subcommand to check
                    {'service': 0x09, 'sub': 0x02},
                    {'service': 0x27, 'sub': 0x01}], # more data "\x07\x03\x00\x00" for this service
        'mode':'UDS'}
    },
    {'mod_stat':    {'pipe': 2}},
     {'hw_USBtin':   {'action': 'write','pipe':2}}
    ]


####### let's see how it looks like from the console...
# > python cantoolz.py -c can_ping_discovery.py
#
# hw_USBtin: Init phase started...
# hw_USBtin: Port found: COM14
# hw_USBtin: PORT: COM14
# hw_USBtin: Speed: 500
# hw_USBtin: USBtin device found!
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
# (0)     -       hw_USBtin               {'action': 'read', 'pipe': 1}           Enabled: True
#                 ||
#                 ||
#                 \/
# (1)     -       mod_stat                {'pipe': 1}             Enabled: True
#                 ||
#                 ||
#                 \/
# (2)     -       gen_ping                {'pipe': 2, 'services': [{'sub': 13, 'service': 1}, {'sub': 2, 'service': 9}, {'data': [7, 3, 0, 0], 'sub': 3, 'service': 47}], 'range': [1790, 1794], 'mode': 'UDS'}           Enabled: False
#                 ||
#                 ||
#                 \/
# (3)     -       mod_stat                {'pipe': 2}             Enabled: True
#
# >>
# >> s                                                     # Start loop
#
# >> c mod_stat p                                         # print stats of what we have
#
# BUS     LEN     ID              MESSAGE                 COUNT
# 60      8       276             1122334455667788        2
# 60      8       277             1122334455667788        4
# >> c 3 p                                     # let's check what we have for now.
#
# >> c 2 s                                     # now start ID bruteforce with UDS requests
# Active status: True                                #
# gen_ping: Loop finished
# >> c 3 p                                     # let's check what we have for now.
#
# BUS     LEN     ID              MESSAGE                 COUNT
# 60      8       276             1122334455667788        230
# 60      8       277             1122334455667788        461
# 60      8       277             1122334455661111        9
# 0       7      1793             062f0307030000          1
# 0       3      1793             020902                  1
# 0       3      1793             02010d                  1
# 0       7      1792             062f0307030000          1
# 0       3      1792             020902                  1
# 0       3      1792             02010d                  1
# 0       7      1791             062f0307030000          1
# 0       3      1791             020902                  1
# 0       3      1791             02010d                  1
# 0       7      1790             062f0307030000          1
# 0       3      1790             020902                  1
# 0       3      1790             02010d                  1
# 60      4      700              0f410d00                6
# 60      8      1803             2f410d0011223344        2
# 60      8      1801             037f1111                2
# 60      4      1799             03410d00                2
# 60      8      1800             1014490201314731        2
# 60      8      1800             215a543533383236        2
# 60      8      1800             2246313039313439        2
#
# >> c 3 a                                    # Let's do analyses of CAN traffic
# ISO TP Messages:
#        ID 1793 and length 6
#        ID 1793 and length 2
#        ID 1793 and length 2
#        ID 1792 and length 6
#        ID 1792 and length 2
#        ID 1792 and length 2
#        ID 1791 and length 6
#        ID 1791 and length 2
#        ID 1791 and length 2
#        ID 1790 and length 6
#        ID 1790 and length 2
#        ID 1790 and length 2
#        ID 1801 and length 3
#        ID 1799 and length 3
#        ID 1800 and length 20
#
#
# UDS found:
#
#         ID: 1792 Service: 0x9 Sub: 0x2 (Req Vehicle info (VIN))
#                 Response: 013147315a54353338323646313039313439 ASCII: .1G1ZT53826F109149
#         ID: 1793 Service: 0x2f Sub: 0x3 (Input Output Control By Identifier)
#                 Error: Service not supported in active session
#         ID: 1791 Service: 0x1 Sub: 0xd (Req Current Powertrain)
#                 Response: 00 ASCII: