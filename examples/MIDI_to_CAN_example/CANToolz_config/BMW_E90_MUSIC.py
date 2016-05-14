load_modules = {
    'hw_USBtin':    {'port':'auto', 'debug':2, 'speed':500},  # IO hardware module

    'ecu_controls':
        {'bus':'BMW_E90',

        'commands':[


			# Music actions
			{'STOP lights': '0x173:8:3afa00022000f2c4', 'cmd':'119'},
			{'High light - ON': '0x1ee:2:10ff', 'cmd':'118'},
			{'High light - blink': '0x1ee:2:20ff', 'cmd':'127'},
			{'CLEANER - once':'0x2a6:2:02a1','cmd':'115'},
			{'Gab. light':'0x12f:8:0d588addf4053001','cmd': '125'},
			{'TURN left':'0x1ee:2:01ff', 'cmd':'124'},
			{'CLEANER + Wasser':'0x2a6:2:10f1','cmd':'116'},
			
			{'Mirrors+windows FOLD':'0x26e:8:5b5b4002ffffffff','cmd':"113"},
			{'Mirrors UNfold':'0x2fc:7:12000000000000','cmd':"112"},
			{'Windows open':'0x26e:8:49494001ffffffff','cmd':"109"},
			{'Trunk open':'0x2a0:8:88888001ffffffff','cmd':"106"},
			{'Trunk close':'0x23a:8:00f310f0fcf0ffff','cmd':"105"}
			
			
			

		],

        'statuses':[


        ]
    }
}

# Now let's describe the logic of this test
actions = [
    {'ecu_controls'     : {}},
    {'hw_USBtin':    {'action':'write','pipe': 1}}
    ]