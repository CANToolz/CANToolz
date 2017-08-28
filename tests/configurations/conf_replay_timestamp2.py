# Test scenario/configuration
modules = {
    'analyze': {'debug': 2},
    'replay': {'load_from': 'tests/data/format.dump', 'debug': 2, 'bus': 'Default'}}
# The test scenario logic
actions = [
    {'replay': {'pipe': 1}},
    {'analyze': {'pipe': 1}}]
