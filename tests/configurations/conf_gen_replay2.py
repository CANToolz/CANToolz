# Test scenario/configuration
modules = {
    'io/hw_fakeIO': {'bus': 31},
    'gen_replay~1': {'debug': 2, 'save_to': 'tests/data/dump2.save', 'load_from': 'tests/data/dump.save'},
    'mod_stat': {'debug': 2}}
# The test scenario logic
actions = [
    {'hw_fakeIO': {'action': 'write', 'pipe': 2}},
    {'gen_replay~1': {'pipe': 2}},
    {'mod_stat': {'pipe': 2}}]
