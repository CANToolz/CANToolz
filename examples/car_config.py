load_modules = {
    ########### Attacker

    #'uds_engine_auth_baypass': {
    #     'id_command': 0x71
    #},

    #'gen_ping' :    {},

    ########### CONTROLS
    #'uds_tester_ecu_engine':{
    #    'id_uds': 0x701,
    #    'uds_shift': 0x08,
    #    'uds_key':''
    #},
    'hw_TCP2CAN':    {'port': 1111, 'mode': 'server', 'address':'127.0.0.1', 'debug':3},
    'hw_TCP2CAN~1':    {'port': 1112, 'mode': 'server','address':'127.0.0.1', 'debug':3},

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

    'control_ecu_lights': {
             'id_report': {0x111:'Left', 0x112:'Right'},
            'id_command': 0x101,
            'commands': {
                'on':'01',
                'off':'00',
                'distance': '02',
            },

            'reports': {
                'LIGHTS ON': 'ff0101',
                'DISTANCE LIGHTS ON': 'ff0202',
                'Lights OFF': '000000'
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
                    0x92,    # Right door status
                    0x111,
                    0x112
                    ],
                'Engine': [0x71]
                },

            'Engine': {

                'OBD2': [
                    0x79,
                    0x709,
                    0x811
                    ],

                'Cabin':[
                    0x79,
                    0x811
                    ]

            },

            'OBD2':  {

                    'Engine':[
                        0x701
                    ],


                }
    },

    'ecu_light~1':{

        'id_report': 0x111,
            'id_command': 0x101,
            'commands': {
                'off':'00',
                'on':'01',
                'distance': '02',
            },

            'reports': {
                'LIGHTS ON': 'ff0101',
                'DISTANCE LIGHTS ON': 'ff0202',
                'Lights OFF': '000000',
            },
            'reports_delay': 1.4

    },

    'ecu_light~2':{

        'id_report': 0x112,
            'id_command': 0x101,
            'commands': {
                'off':'00',
                'on':'01',
                'distance': '02',
            },

            'reports': {
                'LIGHTS ON': 'ff0101',
                'DISTANCE LIGHTS ON': 'ff0202',
                'Lights OFF': '000000',
            },
            'reports_delay': 1.4

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
    'mod_stat':{},
    'mod_stat~2': {}
}


actions = [

    #{'uds_engine_auth_baypass':   {
    #     'action': 'write',
    #     'pipe': 'Engine'}},

    # {'gen_ping':    {                    # Generate UDS requests
    #    'pipe': 'OBD2',
    #    'delay': 0.06,
    #    'range': [1, 2047],           # ID range (from 1790 to 1794)
    #    'services':[{'service': 0x27, 'sub': 0x01}],
    #    'mode':'UDS'}
    #},

     {'ecu_light~1':   {
         'action': 'write',
         'pipe': 'Cabin'}},

     {'ecu_light~2':   {
         'action': 'write',
         'pipe': 'Cabin'}},

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

    #{'uds_tester_ecu_engine': {
    #     'action': 'write',
    #     'pipe': 'OBD2'}},

    {'control_ecu_doors': {
         'action': 'write',
         'pipe': 'Cabin'}},

    {'control_ecu_lights': {
     'action': 'write',
         'pipe': 'Cabin'}},

    {'hw_TCP2CAN':  {'pipe': 'OBD2','action':'read'}},
    {'hw_TCP2CAN~1':  {'pipe': 'Cabin','action':'read'}},

    #{'mod_stat':    {'pipe': 'Cabin', 'no_read': True}},
    #{'mod_stat~2':    {'pipe': 'OBD2', 'no_read': True}},

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


    #{'uds_tester_ecu_engine': {
    #     'action': 'read',
    #     'pipe': 'OBD2'}},




    {'control_ecu_engine': {
         'action': 'read',
         'pipe': 'Engine'}},

    {'control_ecu_doors': {
         'action': 'read',
         'pipe': 'Cabin'}},

    {'control_ecu_lights': {
     'action': 'read',
         'pipe': 'Cabin'}},


    {'ecu_light~1':   {
         'action': 'read',
         'pipe': 'Cabin'}},


    {'ecu_light~2':   {
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

     {'mod_stat':    {'pipe': 'Cabin', 'no_write': True}},
    {'mod_stat~2':    {'pipe': 'OBD2', 'no_write': True}},

   {'hw_TCP2CAN':  {'pipe': 'OBD2','action':'write'}},
    {'hw_TCP2CAN~1':  {'pipe': 'Cabin','action':'write'}}

    ]