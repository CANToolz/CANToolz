import collections
#  Load modules
load_modules = collections.OrderedDict()

load_modules['gen_replay']  = {'load_from': 'tests/replay.save','debug':2,'bus':'allowed'}
load_modules['gen_replay~2'] = {'load_from': 'tests/replay.save','debug':2,'bus':'allowed'}
load_modules['mod_stat'] =  {'debug': 2}
load_modules['mod_stat~1'] =    {'debug': 2}
load_modules['mod_firewall'] =      {'debug': 2}
load_modules['hw_TCP2CAN~server'] =   {'port': 14131, 'mode': 'server','address':'127.0.0.1', 'debug':3}
load_modules['hw_TCP2CAN~client'] = {'port': 14131, 'mode': 'client', 'address':'127.0.0.1', 'debug':3}

# Scenario

actions = [
    {'hw_TCP2CAN~server': {'action':'read'}},
    {'mod_stat':{}},
    {'mod_firewall'     : {'white_bus':[]}},
    {'gen_replay'     : {'pipe':1}},
    {'hw_TCP2CAN~server': {'action':'write'}},

    {'hw_TCP2CAN~client': {'action':'read', 'pipe':2}},
    {'mod_stat':{'pipe': 2}},
    {'mod_firewall'     : {'pipe': 2,'white_bus':[]}},
    {'gen_replay~2'     : {'pipe':2}},
    {'hw_TCP2CAN~client': {'action':'write', 'pipe':2}},

]