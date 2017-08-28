# Test scenario/configuration
modules = {
    'io/hw_USBtin': {'port': 'loop', 'debug': 1, 'speed': 500},
    'ping': {'debug': 1},
    'replay': {'load_from': 'tests/data/test_responses2.save'},
    'analyze': {}}
# The test scenario logic
actions = [
    {'hw_USBtin': {'action': 'read', 'pipe': 1}},
    {'ping': {
        'pipe': 2,
        'range': [1790, 1810],
        'services':[
            {'service': 0x01, 'sub': 0x0d},
            {'service': 0x09, 'sub': 0x02},
            {'service': 0x2F, 'sub': 0x03, 'data': [7, 3, 0, 0]}],
        'mode': 'UDS',
        'padding': 0x41}},
    {'replay': {'pipe': 2}},
    {'analyze': {}},
    {'hw_USBtin': {'action': 'write', 'pipe': 2}}]
