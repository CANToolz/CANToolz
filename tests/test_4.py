#  Load modules
load_modules = {
    'hw_fakeIO'  : {'bus': 31},
    'gen_replay~1'    : {'debug': 2, 'save_to': 'tests/dump2.save', 'load_from':'tests/dump.save'},
    'mod_stat'   : {'debug': 2}
}


# Scenario

actions = [
    {'hw_fakeIO'     : {'action':'write','pipe':2}},
    {'gen_replay~1'      : {'pipe':2}},
    {'mod_stat'   : {'pipe': 2}}
]