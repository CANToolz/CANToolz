# Test scenario/configuration
modules = {
    'io/hw_USBtin': {'port': 'loop', 'debug': 1, 'speed': 500},
    'replay': {'debug': 1, 'load_from': 'tests/data/test_responses.save'},                             # Module for sniff and replay
    'analyze': {}}
# The test scenario logic
actions = [
    {'hw_USBtin': {'action': 'read', 'pipe': 1}},
    {'replay': {'pipe': 2}},
    {'analyze': {}},
    {'hw_USBtin': {'action': 'write', 'pipe': 2}}]
