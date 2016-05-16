load_modules = {
    'hw_USBtin':    {'port':'auto', 'debug':2, 'speed':500},  # IO hardware module

    'ecu_controls':
        {'bus':'BMW_F10',

        'commands':[


			# Music actions

			

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