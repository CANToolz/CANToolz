
load_modules = {
    'hw_CANBusTriple':    {
        'port':'auto',
        'bus_1': 1,    # CBT bus 1
        'bus_2': 2,    # CBT bus 2 MITM mode (by default bus_2 = bus_1, no MITM)
        'debug': 2,
        'speed':500}, # IO hardware module
    'mod_stat':    {},                                      # Mod stat
    'mod_firewall':    {'debug': 1}                            # Generator/Ping
}

actions = [
    {'hw_CANBusTriple':   {'action': 'read'}}, # Read from bus_1 and bus_2
    {'mod_firewall':      {'black_list': [133, 555, 1111]}}, # Block chosen frames by ID
    {'mod_stat':          {}},                            # read not blocked packets from both buses
    {'hw_CANBusTriple':   {'action': 'write'}}            # Write packets back but in different buses (MITM)
    ]


# hw_CANBusTriple: Init phase started...
# hw_CANBusTriple: Port found: COM11
# hw_CANBusTriple: Port : COM11
# hw_CANBusTriple: Bus 1: 1
# hw_CANBusTriple: Bus 2: 2
# hw_CANBusTriple: Speed: 500
# hw_CANBusTriple: CANBus Triple device detected, version: 0.4.4
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
# (0)     -       hw_CANBusTriple {'action': 'read', 'pipe': 1}           Enabled: True
#                 ||
#                 ||
#                 \/
# (1)     -       mod_firewall            {'pipe': 1, 'black_list': [133, 555, 1111]}             Enabled: True
#                 ||
#                 ||
#                 \/
# (2)     -       mod_stat                {'pipe': 1}             Enabled: True
#                 ||
#                 ||
#                 \/
# (3)     -       hw_CANBusTriple {'action': 'write', 'pipe': 1}          Enabled: True
# >> s                                                          # start MITM
