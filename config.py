load_modules = {'hw_CANSocket':{'iface': 'vcan0', 'debug':1},'mod_stat':{},'gen_ping':{}}

actions = [
{'hw_CANSocket': {'action':'read'}},

{'mod_stat': {}},
     {'gen_ping':    {                    # Generate UDS requests
        'pipe': 2,
        'range': [1, 3],           # ID range (from 1790 to 1794)
        'services':[{'service': 0x10, 'sub': 0x01},
                    {'service': 0x3E, 'sub': None},
                    {'service': 0x3E, 'sub': 0x01}],
        'mode':'UDS'}},
{'hw_CANSocket': {'action':'write'}}
]
