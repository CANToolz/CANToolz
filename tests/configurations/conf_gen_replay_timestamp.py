# Test scenario/configuration
modules = {
    'mod_stat': {'debug': 2},
    'gen_replay': {'load_from': 'tests/data/replay_format.save', 'debug': 2, 'bus': 'Default'}}
# The test scenario logic
actions = [
    {'gen_replay': {'pipe': 1}},
    {'mod_stat': {'pipe': 1}}]
