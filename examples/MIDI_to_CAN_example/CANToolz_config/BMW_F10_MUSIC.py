modules = {
    'io/hw_USBtin':    {'port':'auto', 'debug':2, 'speed':500},  # IO hardware module

    'ecu_controls':
        {'bus':'BMW_F10',

        'commands':[


			# Music actions
			
			{'High light - blink': '0x1ee:2:20ff', 'cmd':'127'},
			{'TURN LEFT and RIGHT': '0x2fc:7:31000000000000', 'cmd':'126'},
			{'TURN right ON PERMANENT': '0x1ee:2:01ff', 'cmd':'124'},
			{'TURN right x3 or OFF PERMANENT':'0x1ee:2:02ff','cmd':'123'},
			{'TURN left ON PERMANENT': '0x1ee:2:04ff', 'cmd':'122'},
			{'TURN left x3 or OFF PERMANENT':'0x1ee:2:08ff','cmd':'121'},
			{'STOP lights': '0x173:8:3afa00022000f2c4', 'cmd':'120'},


			{'CLEANER - once':'0x2a6:2:02a1','cmd':'119'},
			{'CLEANER x3 + Wasser':'0x2a6:2:10f1','cmd':'118'},
			{'Mirrors+windows FOLD':'0x26e:8:5b5b4002ffffffff','cmd':"117"},
			{'Mirrors UNfold':'0x2fc:7:12000000000000','cmd':"116"},
			{'Windows open':'0x26e:8:49494001ffffffff','cmd':"115"},
			{'Windows rear close + Mirrors FOLD':'0x26e:8:405b4002ffffffff','cmd':"114"},
			{'Trunk open':'0x2a0:8:88888001ffffffff','cmd':"113"},
			{'Trunk close':'0x23a:8:00f310f0fcf0ffff','cmd':"112"}
			

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
