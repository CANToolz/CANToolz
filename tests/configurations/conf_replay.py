# Test scenario/configuration
modules = {
    'io/hw_fakeIO': {'bus': 31},
    'replay': {'debug': 2, 'save_to': 'tests/data/dump.save'},
    'analyze': {'debug': 2}}
# The test scenario logic
actions = [
    {'hw_fakeIO': {'action': 'write', 'pipe': 2}},
    {'replay': {'pipe': 2}},
    {'analyze': {'pipe': 2}}]
