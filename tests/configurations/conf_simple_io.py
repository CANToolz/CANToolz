# Test scenario/configuration
modules = {
    'io/hw_USBtin': {'port': 'loop', 'debug': 2, 'speed': 500},
    'io/simple_io': {'bus': 'TEST_1'},
    'firewall': {},
    'analyze': {}}
# The test scenario logic
actions = [
    {'hw_USBtin': {'action': 'read', 'pipe': 1}},
    {'simple_io': {}},
    {'analyze': {}},
    {'firewall': {'white_bus': ['TEST_1']}},
    {'hw_USBtin': {'action': 'write', 'pipe': 1}}]
