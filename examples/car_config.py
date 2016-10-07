load_modules = {
    ########### Attacker

    'uds_engine_auth_baypass': {
         'id_command': 0x71
    },

    ########### CONTROLS
    'uds_tester_ecu_engine':{
        'id_uds': 0x701,
        'uds_shift': 0x08,
        'uds_key':''
    },

    'control_ecu_doors': {
            'id_report': {0x91:'Left', 0x92:'Right'},
            'id_command': 0x81,
            'commands': {
                'lock':'1000',
                'unlock':'10ff',
                'init': '00ff',
            },

            'reports': {
                'Locked': '2000',
                'Unlocked': '20ff'
            }
    },
    'control_ecu_engine': {

        'id_report': 0x79,
        'id_command': 0x71,
        'vin':'NLXXX6666CW006666',
        'start_uniq_key':'tGh&ujKnf5$rFgvc%',
        'commands': {
                'rpm_up':'01',
                'rpm_down':'02',
                'init': '',
                'stop': '00'
            }

    },

    ########### CAR
    'ecu_switch':    {

            'Cabin': {   # From Cabin interface

                'OBD2':[    # To OBD2 allowed next ID
                    0x91,   # Left door  status
                    0x92    # Right door status
                    ],

                },

            'Engine': {

                'OBD2': [
                    0x79,
                    0x709,
                    0x811
                    ],

                'Cabin':[
                    0x79
                    ]

            },

            'OBD2':  {

                    'Engine':[
                        0x701
                    ],


                }
    },

    'ecu_door~1':    {

        'id_report': 0x91,
            'id_command': 0x81,
            'commands': {
                'lock':'1000',
                'unlock':'10ff',
                'init': '00ff',
            },

            'reports': {
                'Locked': '2000',
                'Unlocked': '20ff'
            },
            'reports_delay': 0.9
        },
    'ecu_door~2':    {

        'id_report': 0x92,
            'id_command': 0x81,
            'commands': {
                'lock':'1000',
                'unlock':'10ff',
                'init': '00ff',
            },

            'reports': {
                'Locked': '2000',
                'Unlocked': '20ff'
            },
            'reports_delay': 0.9
        },

    'ecu_engine':    {

        'id_report': 0x79,
        'id_uds': 0x701,
        'uds_shift': 0x08,
        'id_command': 0x71,
        'vin_id': 0x811,
        'vin':'NLXXX6666CW006666',
        'start_uniq_key':'tGh&ujKnf5$rFgvc%',
        'uds_key':'secret_uds_auth',
        'commands': {
                'rpm_up':'01',
                'rpm_down':'02',
                'init': '',
                'stop': '00'
            },

        'reports_delay': 0.2

    },
    'mod_stat':{}
}


actions = [

    {'uds_engine_auth_baypass':   {
         'action': 'write',
         'pipe': 'Engine'}},

    {'ecu_door~1':   {
         'action': 'write',
         'pipe': 'Cabin'}},

    {'ecu_door~2':   {
         'action': 'write',
         'pipe': 'Cabin'}},

    {'ecu_engine':   {
         'action': 'write',
         'pipe': 'Engine'}},

    {'control_ecu_engine': {
         'action': 'write',
         'pipe': 'Engine'}},

    {'uds_tester_ecu_engine': {
         'action': 'write',
         'pipe': 'OBD2'}},

    {'control_ecu_doors': {
         'action': 'write',
         'pipe': 'Cabin'}},

                {'ecu_switch':   {
                     'action': 'read',
                     'pipe': 'OBD2'}},

                {'ecu_switch':   {
                     'action': 'read',
                     'pipe': 'Cabin'}},

                {'ecu_switch':   {
                     'action': 'read',
                     'pipe': 'Engine'}},

                {'ecu_switch':   {
                     'action': 'write',
                     'pipe': 'OBD2'}},

                {'ecu_switch':   {
                     'action': 'write',
                     'pipe': 'Cabin'}},

                {'ecu_switch':   {
                     'action': 'write',
                     'pipe': 'Engine'}},

    {'control_ecu_engine': {
         'action': 'read',
         'pipe': 'Engine'}},

    {'uds_tester_ecu_engine': {
         'action': 'read',
         'pipe': 'OBD2'}},

    {'control_ecu_doors': {
         'action': 'read',
         'pipe': 'Cabin'}},

    {'ecu_door~1':   {
         'action': 'read',
         'pipe': 'Cabin'}},

    {'ecu_door~2':   {
         'action': 'read',
         'pipe': 'Cabin'}},

    {'ecu_engine':   {
         'action': 'read',
         'pipe': 'Engine'}},


    {'mod_stat':    {'pipe': 'OBD2'}}
    #{'mod_stat':    {'pipe': 'Cabin'}},
    #{'mod_stat':    {'pipe': 'Engine'}}

    ]