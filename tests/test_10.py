load_modules = {
    'hw_USBtin':    {'port':'loop', 'debug':2, 'speed':500},  # IO hardware module

    'simple_io':
        {'bus':'TEST_1'},
    'mod_firewall': {},
    'mod_stat':    {}

}

# Now let's describe the logic of this test
actions = [
    {'hw_USBtin':   {'action': 'read','pipe': 1}},
    {'simple_io'     : {}},
    {'mod_stat':{}},
    {'mod_firewall': {'white_bus': ['TEST_1']}},
    {'hw_USBtin':    {'action':'write','pipe': 1}}
    ]