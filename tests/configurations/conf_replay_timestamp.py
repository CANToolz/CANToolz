# Test scenario/configuration
modules = {
    'analyze': {'debug': 2},
    'replay': {'load_from': 'tests/data/replay_format.save', 'debug': 2, 'bus': 'Default'}}
# The test scenario logic
actions = [
    {'replay': {'pipe': 1}},
    {'analyze': {'pipe': 1}}]
