load_modules = {'hw_CANSocket':{'iface': 'vcan0', 'debug':2},'mod_stat':{}}

actions = [
{'hw_CANSocket': {'action':'read'}},
{'mod_stat': {}}
]
