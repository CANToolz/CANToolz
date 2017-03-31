load_modules = {
    'hw_CAN232': {'port': '/dev/cu.usbmodem1421', 'speed': '500KBPS', 'serial_speed': 115200, 'debug': 3},
    'mod_stat': {'debug': 0},
}

actions = [
    {'hw_CAN232': {'action': 'read', 'pipe': 1}},
    {'mod_stat': {'pipe': 1}},
]
