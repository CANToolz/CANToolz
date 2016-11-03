#  Load modules
load_modules = {
    'hw_fakeIO'  : {'debug':2, 'bus': 31},
    'hw_fakeIO~1'    : {'debug': 2, 'bus': 32},
    'mod_firewall'     : {'debug': 2},
    'mod_stat'   : {'debug': 2}
}


# Scenario

actions = [
    {'hw_fakeIO'     : {'action': 'write', 'pipe': 2}},
    {'mod_stat'      : {'pipe': 1}},
    {'mod_firewall'     : {'pipe': 2}},
    {'hw_fakeIO~1'   : {'action': 'read', 'pipe': 2}}

]