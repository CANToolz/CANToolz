# Test scenario/configuration
modules = {
    'io/hw_USBtin': {'port': 'loop', 'debug': 2, 'speed': 500},
    'can_controls': {
        'bus': 'ECU_TEST',
        'commands': [
            {'cmd': 'a', 'Unlock': '0x122:2:fff0'},
            {'cmd': 'b', 'Lock': '0x122:2:ffff'},
            {'cmd': 'c', 'Open Trunk': '290:2:ffa0'}],
        'statuses': [
            {'cmd': 'd', 'Door - Rear passenger': {'Open': '0x133#ff.*', 'Closed': '0x133#00.*'}},
            {'cmd': 'e', 'Door - Front driver': {'Open': '0x133#..FF.*', 'Closed': '0x133#..00.*'}}]
    },
    'mod_firewall': {},
    'mod_stat': {'debug': 2},
    'mod_stat~2': {'debug': 2}
}
# Logic of the test scenario
actions = [
    {'hw_USBtin': {'action': 'read', 'pipe': 1}},
    {'can_controls': {}},
    {'mod_stat': {}},
    {'mod_firewall': {'white_bus': ['ECU_TEST']}},
    {'mod_stat~2': {}},
    {'hw_USBtin': {'action': 'write', 'pipe': 1}}]
