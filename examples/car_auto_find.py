
modules = {
    'io/hw_TCP2CAN':    {'port': 1112, 'mode': 'client', 'address':'127.0.0.1', 'debug':3},                # IO hardware module
    'firewall':    {},
    'analyze':    {'bus':'statcheck'}
}

actions = [

    {'hw_TCP2CAN':   {'action': 'read'}}, # Read to PIPE 1
    {'analyze':    {}},
    {'firewall':    {'white_bus':['statcheck']}},
    {'hw_TCP2CAN':   {'action': 'write'}},



    ]


