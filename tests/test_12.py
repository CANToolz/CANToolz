
#  Load modules
load_modules = {
    'mod_stat'    : {'debug': 2},
    'gen_replay'   : {'load_from': 'tests/format.dump','debug':2,'bus':'Default'}
}


# Scenario

actions = [
    {'gen_replay'     : {'pipe':1}},
    {'mod_stat':{'pipe': 1}}

]