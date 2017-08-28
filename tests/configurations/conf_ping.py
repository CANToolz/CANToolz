# Test scenario/configuration
modules = {
    'io/hw_fakeIO': {'bus': 31},
    'ping': {'debug': 2, 'bus': 32},
    'ping~1': {'debug': 2},
    'analyze': {'debug': 2}}
# The test scenario logic
actions = [
    {'ping': {'pipe': 2}},
    {'ping~1': {'pipe': 1}},
    {'hw_fakeIO': {'action': 'write', 'pipe': 2}},
    {'analyze': {'pipe': 2}}, {'analyze': {'pipe': 1}}]
