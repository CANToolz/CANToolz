modules = {
    'io/hw_TCP2CAN':    {'port': 1111, 'mode': 'server', 'address':'127.0.0.1', 'debug':3},
    'io/hw_TCP2CAN~1':    {'port': 1112, 'mode': 'server','address':'127.0.0.1', 'debug':3},

    'vircar/anti_theft_1':{

        'filter': [0x71],
        'commands': {
                '0x101:1:01':'one',
                '0x101:1:02':'two',
                '0x101:1:00':'three'
            },
        'pass_seq':['one','one','two','one','three','two','three'] # Passcode sequence

    },

    'vircar/anti_theft_2':{
        'stop_engine': '0x71:1:00',
        'filter': [0x71],
        'commands': {
                '0x101:1:01':'one',
                '0x101:1:02':'two',
                '0x101:1:00':'three'
            },
        'pass_seq':['one','one','two','one','three','two','three'] # Passcode sequence

    },

    'vircar/control_ecu_doors': {
            'id_report': {0x91:'Left', 0x92:'Right'},
            'id_command': 0x81,
            'commands': {
                'lock':'1000',
                'unlock':'1002',
                'init': '00ff',
            },

            'reports': {
                'Locked': '2000',
                'Unlocked': '20ff'
            }
    },

    'vircar/control_ecu_lights': {
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

    'vircar/control_ecu_engine': {

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
    'vircar/ecu_switch':    {

            'Cabin': {   # From Cabin interface

                'OBD2':[    # To OBD2 allowed next ID
                    0x91,   # Left door  status
                    0x92,    # Right door status
                    0x111,
                    0x112
                    ],
                'Engine': [0x71,0x101]
                },

            'Engine': {

                'OBD2': [
                    0x79,
                    0x709,
                    0x811
                    ],

                'Cabin':[
                    0x71,
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

    'vircar/ecu_light~1':{

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
            'reports_delay': 0.4

    },

    'vircar/ecu_light~2':{

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
            'reports_delay': 0.4

    },

    'vircar/ecu_door~1':    {

        'id_report': 0x91,
            'id_command': 0x81,
            'commands': {
                'lock':'1000',
                'unlock':'1002',
                'init': '00ff',
            },

            'reports': {
                'Locked': '2000',
                'Unlocked': '20ff'
            },
            'reports_delay': 0.5
        },
    'vircar/ecu_door~2':    {

        'id_report': 0x92,
            'id_command': 0x81,
            'commands': {
                'lock':'1000',
                'unlock':'1002',
                'init': '00ff',
            },

            'reports': {
                'Locked': '2000',
                'Unlocked': '20ff'
            },
            'reports_delay': 0.5
        },

    'vircar/ecu_engine':    {

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
    'analyze':{},
    'analyze~2': {}
}


actions = [

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

    {'control_ecu_doors': {
         'action': 'write',
         'pipe': 'Cabin'}},

    {'control_ecu_lights': {
     'action': 'write',
         'pipe': 'Cabin'}},

            #{'anti_theft_2': {'pipe':'Cabin','action':'write'}},

    {'hw_TCP2CAN':  {'pipe': 'OBD2','action':'read'}},  # read from TCP
    {'hw_TCP2CAN~1':  {'pipe': 'Cabin','action':'read'}},

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


    {'hw_TCP2CAN':  {'pipe': 'OBD2','action':'write'}},  # Write to TCP
    {'hw_TCP2CAN~1':  {'pipe': 'Cabin','action':'write'}},

            #{'anti_theft_2': {'pipe':'Cabin','action':'read'}},

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

       # {'anti_theft_1': {'pipe':'Engine', 'action':'read'}},
       # {'anti_theft_1': {'pipe':'Engine', 'action':'write'}}, # MITM

    {'ecu_engine':   {
         'action': 'read',
         'pipe': 'Engine'}},



    ]
