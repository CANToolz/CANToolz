# Load needed modules
modules = {
    'io/hw_USBtin':    {'port':'loop', 'debug':1, 'speed':500},                # IO hardware module connected to first BUS (IVI)
    'io/hw_USBtin~2':  {'port':'loop', 'debug':1, 'speed':500, 'bus': 62 },    # IO hardware module (connected to OBD2)
    'ping' :    {},                                                     # Generator/Ping
    'firewall': {},                                                     # We need firewall to block all other packets
    'analyze':     {}                                                      # Mod stat to see results
}

actions = [
    {'hw_USBtin':    {'action': 'read','pipe': 1}},     # Read to PIPE 1 from IVI
    {'hw_USBtin~2':  {'action': 'read','pipe': 2}},     # Read to PIPE 2 from OBD2 port
    {'firewall': {'white_body':[[1,2,3,4,5,6,7,8]],'pipe': 1}}, # Block all other CAN frames, but let frames with
                                                                  #  data "\x01\x02\x03\x04\x05\x06\x07\x08" pass
    {'firewall': {'white_body':[[1,2,3,4,5,6,7,8]], 'pipe': 2}},

    {'analyze': {'pipe': 1}}, {'analyze': {'pipe': 2}}, # read from both pipes after filtration

    {'ping': {'range': [1,2000],'mode':'CAN','body':'0102030405060708','pipe':3, 'delay':0.06}},
                                                         # Generate CAN frames to PIPE 3
    {'hw_USBtin': {'pipe': 3, 'action': 'write'}},         # Write generated packets to both buses
    {'hw_USBtin~2': {'pipe': 3, 'action': 'write'}}
    ]

####### let's see how it looks like from the console...
# > python cantoolz.py -c can_switch_scanner.py
# hw_USBtin: Port found: COM14
# hw_USBtin: PORT: COM14
# hw_USBtin: Speed: 500
# hw_USBtin: USBtin device found!
# hw_USBtin: Init phase started...
# hw_USBtin: Error opening port: COM14
# hw_USBtin: Port found: COM13
# hw_USBtin: PORT: COM13
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
# (0)     -       hw_USBtin               {'action': 'read', 'pipe': 1}           Enabled: True
#                 ||
#                 ||
#                 \/
# (1)     -       hw_USBtin~2             {'action': 'read', 'pipe': 2}           Enabled: True
#                 ||
#                 ||
#                 \/
# (2)     -       firewall            {'pipe': 1, 'white_body': [[1, 2, 3, 4, 5, 6, 7, 8]]}          Enabled: True
#                 ||
#                 ||
#                 \/
# (3)     -       firewall            {'pipe': 2, 'white_body': [[1, 2, 3, 4, 5, 6, 7, 8]]}          Enabled: True
#                 ||
#                 ||
#                 \/
# (4)     -       analyze                {'pipe': 1}             Enabled: True
#                 ||
#                 ||
#                 \/
# (5)     -       analyze                {'pipe': 2}             Enabled: True
#                 ||
#                 ||
#                 \/
# (6)     -       ping                {'body': '0102030405060708', 'pipe': 3, 'range': [1, 2000], 'mode': 'CAN'}              Enabled: False
#                 ||
#                 ||
#                 \/
# (7)     -       hw_USBtin               {'pipe': 3, 'action': 'write'}          Enabled: True
#                 ||
#                 ||
#                 \/
# (8)     -       hw_USBtin~2             {'pipe': 3, 'action': 'write'}          Enabled: True
#
# >> start                          # start
# >> c 6 s                          # send data to first and second BUS  (OBDII/IVI)
# Active status: True
# >> c 4 p                  # Let see passed frames (good targets)
#
# BUS     ID      LENGTH          MESSAGE                 COUNT
# 60      1311    8               0102030405060708        1        # These frames  (BUS 60) not filtered by CAN Switch
# 60      1615    8               0102030405060708        1        #  and it is mean you can send data from OBD2
# 60      1205    8               0102030405060708        1        #    to HeadUnit (IVI)
# 62      1313    8               0102030405060708        1
# 62      723     8               0102030405060708        1
# 62      619     8               0102030405060708        1
# 60      1121    8               0102030405060708        1
# 62      1600    8               0102030405060708        1
# 62      1129    8               0102030405060708        1
# 60      1223    8               0102030405060708        1
# 62      1319    8               0102030405060708        1        # And those ()BUS 62 passed from HU to OBD2
# 62      1696    8               0102030405060708        1
# 62      1600    8               0102030405060708        1
# 62      1129    8               0102030405060708        1


