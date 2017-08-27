# Test scenario/configuration
modules = {
    'hw_USBtin': {'port': 'loop', 'debug': 1, 'speed': 500},
    'gen_replay': {'debug': 1, 'load_from': 'tests/data/test_responses.save'},                             # Module for sniff and replay
    'mod_stat': {}}
# The test scenario logic
actions = [
    {'hw_USBtin': {'action': 'read', 'pipe': 1}},
    {'gen_replay': {'pipe': 2}},
    {'mod_stat': {}},
    {'hw_USBtin': {'action': 'write', 'pipe': 2}}]
