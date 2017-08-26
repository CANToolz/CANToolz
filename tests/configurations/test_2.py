
#  Load modules
load_modules = {
    'hw_fakeIO'  : {'bus': 31},
    'gen_ping'    : {'debug': 2, 'bus': 32},
    'gen_ping~1'     : {'debug': 2},
    'mod_stat'   : {'debug': 2}
}


# Scenario

actions = [
    {'gen_ping'     : {'pipe': 2}},
    {'gen_ping~1'      : {'pipe': 1}},
    {'hw_fakeIO'     : {'action':'write','pipe':2}},
    {'mod_stat'   : {'pipe': 2}}, {'mod_stat'   : {'pipe': 1}}

]