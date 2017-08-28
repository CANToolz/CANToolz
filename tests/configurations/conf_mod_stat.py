# Test scenario/configuration
modules = {
    'io/hw_fakeIO': {'debug': 2, 'bus': 31},
    'io/hw_fakeIO~1': {'debug': 2, 'bus': 32},
    'mod_firewall': {'debug': 2},
    'mod_stat': {'debug': 2}}
# The test scenario logic
actions = [
    {'hw_fakeIO': {'action': 'write', 'pipe': 2}},
    {'mod_stat': {'pipe': 1}},
    {'mod_firewall': {'pipe': 2}},
    {'hw_fakeIO~1': {'action': 'read', 'pipe': 2}}]
