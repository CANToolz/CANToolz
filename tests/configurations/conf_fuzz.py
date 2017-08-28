# Test scenario/configuration
modules = {
    'fuzz': {},
    'pipe_switch': {},
    'analyze': {}}
# The test scenario logic
actions = [
    {'fuzz': {}},
    {'pipe_switch': {'action': 'read'}},
    {'pipe_switch': {'action': 'write', 'pipe': 3}},
    {'analyze': {'pipe': 3}}]
