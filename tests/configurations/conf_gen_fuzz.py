# Test scenario/configuration
modules = {
    'gen_fuzz': {},
    'pipe_switch': {},
    'mod_stat': {}}
# The test scenario logic
actions = [
    {'gen_fuzz': {}},
    {'pipe_switch': {'action': 'read'}},
    {'pipe_switch': {'action': 'write', 'pipe': 3}},
    {'mod_stat': {'pipe': 3}}]
