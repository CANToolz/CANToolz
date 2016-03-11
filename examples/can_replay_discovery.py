#  This example just like "Using can-utils to Find the Door-Unlock Control"
#  from great book: "The Car Hacker's Handbook The Car Hacker's
#      Handbook A Guide for the Penetration Tester" by Craig Smith

# Load needed modules
load_modules = {
    'hw_USBtin':    {'port':'auto', 'debug':1, 'speed':500},  # IO hardware module
    'gen_replay':   {'debug': 1},                             # Module for sniff and replay
    'mod_stat':    {}                                         # Stats
}

# Now let's describe the logic of this test
actions = [
    {'hw_USBtin':   {'action': 'read','pipe': 1}},   # Read to PIPE 1
    {'gen_replay':    {'pipe': 1}},                  # We will sniff first from PIPE 1, then replay to PIPE 2
    {'hw_USBtin':    {'action':'write','pipe': 2}}   # Write generated packets (pings)
    ]

####### let's see how it looks like from the console...
# python canstoolz.py -c can_replay_discovery.py
# hw_USBtin: Init phase started...
# hw_USBtin: Port found: COM14
# hw_USBtin: PORT: COM14
# hw_USBtin: Speed: 500
# hw_USBtin: USBtin device found!
#
#
#   _____          _   _ _______          _
#  / ____|   /\   | \ | |__   __|        | |
# | |       /  \  |  \| |  | | ___   ___ | |____
# | |      / /\ \ | . ` |  | |/ _ \ / _ \| |_  /
# | |____ / ____ \| |\  |  | | (_) | (_) | |/ /
#  \_____/_/    \_\_| \_|  |_|\___/ \___/|_/___|
#
#
#
# >> v
# Loaded queue of modules:
#
# (0)     -       hw_USBtin               {'action': 'read', 'pipe': 1}           Enabled: True
#                ||
#                ||
#                \/
# (1)     -       gen_replay              {'pipe': 1}             Enabled: True
#                ||
#                ||
#                \/
# (2)     -       hw_USBtin               {'action': 'write', 'pipe': 2}          Enabled: True
#
# >> s                            # start main loop
# >> c 1 g               # collect CAN traffic
# True
# >> c 1 g               # after some time when 'action' finished stop collecting traffic
# False
# >> c 1 p               # see amount of collected packets (you can use mod_stat additional for more info) .. a lot of things there
# >> 28790
# >> stop
# >> e 1 {'pipe':2}      # switch to pipe 2
# >> s
# >> c 1 0-14000         # let's replay firsts half.. does action happen?
# >> True
# >> c 1 14000-28790     # if not then second half...
# >> True
# >> c 1 14000-20000     # And continue our 'binary' search
# >> True
# >> c 1 18000-20000     # And continue our 'binary' search
# >> True
# >> c 1 18000-19000    # And continue our 'binary' search
# >> True
# .....
# >> c 1 18500-18550    # here we are...
# >> True
# >> c 1 d 18500-18550  # dump chosen range into a file
