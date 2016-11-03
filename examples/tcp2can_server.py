
load_modules = {
    'hw_TCP2CAN':    {'port': 1111, 'mode': 'server','address':'127.0.0.1', 'debug':3},                # IO hardware module
    'hw_USBtin':    {'port':'auto', 'debug':1, 'speed':500},
    'mod_stat':    {}
}

actions = [

    {'hw_USBtin':   {'action': 'read'}},
    {'hw_TCP2CAN':   {'action': 'write'}}, # Read to PIPE 1
    {'mod_stat':    {'pipe': 1}},
    {'hw_TCP2CAN':   {'action': 'read','pipe':2}}, # Read to PIPE 1
    {'hw_USBtin':   {'action': 'write','pipe':2}},
    {'mod_stat':    {'pipe': 2}}

    ]


