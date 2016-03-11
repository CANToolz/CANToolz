#  Load modules
load_modules = {
    'gen_ping'  : {},
    'gen_ping~2'    : {},
    'hw_fakeIO'     : {'bus': 11},
    'hw_fakeIO~2'   : {'bus': 22},
    'mod_stat'      : {'debug': 2}

}


# Scenario

actions = [
    {'gen_ping'      : {'pipe': 1}},

    {'gen_ping~2'    : {
        'pipe':1,
        'range': [1790, 1791],
        'services': [
            {'service':0x01, 'sub':0x0d},
            {'service':0x09, 'sub':0x02},
            {'service':0x2F, 'sub':0x03, 'data':[7,3,0,0]}
        ],
        'mode': 'UDS'}},

    {'hw_fakeIO'     : {'action':'write','pipe': 2}},
    {'hw_fakeIO~2'   : {'action':'write','pipe': 1}},

    {'hw_fakeIO'     : {'action':'read','pipe': 2}},

    {'hw_fakeIO~2'   : {'action':'read','pipe': 1}},

    {'mod_stat' : {'pipe': 1}}, {'mod_stat' : {'pipe': 2}}
]
