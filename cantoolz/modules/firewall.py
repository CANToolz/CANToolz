from cantoolz.module import CANModule


class firewall(CANModule):

    name = "Filter CAN messages"
    help = """

    This module block CAN messages by ID.

    Init parameters:  None

    Module parameters:

      'white_list' - list of ID that should be filtered
      'black_list' - list of ID that should not be filtered
      'pipe'       - integer, 1 or 2 - from which pipe to print, default 1

      Example: {'white_list':[133,111]}

    """

    id = 4
    _active = True
    version = 1.0

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can, args):
        if can.data is not None:
            if 'black_list' in args and can.id in args.get('black_list', []):
                can.data = None
                self.dprint(2, "Message " + str(can.id) + " has been blocked(BL) (BUS = " + str(can.bus) + ")")
            elif 'white_list' in args and can.id not in args.get('white_list', []):
                can.data = None
                self.dprint(2, "Message " + str(can.id) + " has been blocked(WL) (BUS = " + str(can.bus) + ")")
            if 'white_body' in args and can.data not in args.get('white_body', []):
                can.data = None
                self.dprint(2, "Message " + str(can.id) + " has been blocked(WB) (BUS = " + str(can.bus) + ")")
            elif 'black_body' in args and can.data in args.get('black_body', []):
                can.data = None
                self.dprint(2, "Message " + str(can.id) + " has been blocked(BB) (BUS = " + str(can.bus) + ")")
            if 'hex_white_body' in args and self.get_hex(can.raw_data) not in args.get('hex_white_body', []):
                can.data = None
                self.dprint(2, "Message " + str(can.id) + " has been blocked(WB) (BUS = " + str(can.bus) + ")")
            elif 'hex_black_body' in args and self.get_hex(can.raw_data) in args.get('hex_black_body', []):
                can.data = None
                self.dprint(2, "Message " + str(can.id) + " has been blocked(BB) (BUS = " + str(can.bus) + ")")
            if 'black_bus' in args and can.bus.strip() in args.get('black_body', []):
                can.data = None
                self.dprint(2, "Message " + str(can.id) + " has been blocked(BBus) (BUS = " + str(can.bus) + ")")
            elif 'white_bus' in args and can.bus.strip() not in args.get('white_bus', []):
                can.data = None
                self.dprint(2, "Message " + str(can.id) + " has been blocked(WBus) (BUS = " + str(can.bus) + ")")
        return can
