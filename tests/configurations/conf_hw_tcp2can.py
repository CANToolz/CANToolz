import collections

# Test scenario/configuration
modules = collections.OrderedDict()
modules['replay'] = {'load_from': 'tests/data/replay.save', 'debug': 2, 'bus': 'allowed'}
modules['replay~2'] = {'load_from': 'tests/data/replay.save', 'debug': 2, 'bus': 'allowed'}
modules['analyze'] = {'debug': 2}
modules['analyze~1'] = {'debug': 2}
modules['firewall'] = {'debug': 2}
modules['io/hw_TCP2CAN~server'] = {'port': 14131, 'mode': 'server', 'address': '127.0.0.1', 'debug': 3}
modules['io/hw_TCP2CAN~client'] = {'port': 14131, 'mode': 'client', 'address': '127.0.0.1', 'debug': 3}
# The test scenario logic
actions = [
    {'hw_TCP2CAN~server': {'action': 'read'}},
    {'analyze': {}},
    {'firewall': {'white_bus': []}},
    {'replay': {'pipe': 1}},
    {'hw_TCP2CAN~server': {'action': 'write'}},

    {'hw_TCP2CAN~client': {'action': 'read', 'pipe': 2}},
    {'analyze': {'pipe': 2}},
    {'firewall': {'pipe': 2, 'white_bus': []}},
    {'replay~2': {'pipe': 2}},
    {'hw_TCP2CAN~client': {'action': 'write', 'pipe': 2}}]
