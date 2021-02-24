import time

from cantoolz.can import CANMessage
from cantoolz.uds import UDSMessage
from cantoolz.isotp import ISOTPMessage
from cantoolz.module import CANModule


class ping(CANModule):

    name = "Sending CAN pings"
    help = """

    This module doing ID buteforce.
    (combine with analyze for example)
    Init parameters: None
    Module parameters:
       body           -  data HEX that will be used in CAN for discovery (by default body is 0000000000000000)
       mode           -  by default CAN, but also support ISOTP and UDS
       range          -  [0,1000] - ID range
       delay          - delay between frames (0 by default)
         {'body':'0011223344556677889900aabbccddeeff','mode':'isotp'}  ; ISO-TP
         {'body':'001122334455667788','mode':'CAN'}  ; ISO-TP
         {'services':[{'service':0x01, 'sub':0x0d},{'service':0x09, 'sub':0x02},{'service':0x2F, 'sub':0x03, 'data':[7,3,0,0]}],'mode':'UDS'}  ; UDS
    """

    queue_messages = []

    def do_init(self, params):
        self._active = False
        self._last = 0
        self._full = 1

    def get_status(self):
        return "Current status: " + str(self._active) + "\nFrames in queue: " + str(len(self.queue_messages))

    def do_ping(self, params):
        if not self.queue_messages:
            self._active = False
            self.do_start(params)
            return None

        return self.queue_messages.pop()

    @staticmethod
    def _get_iso_mode(args):
        """Get the ISO mode from the action parameters.

        :param dict args: Actions parameters

        :return: ISO mode. 0: CAN; 1: ISO-TP; 2: UDS
        :rtype: int
        """
        ret = 0
        mode = args.get('mode', '').lower()
        if mode.startswith('iso'):
            ret = 1
        elif mode.startswith('uds'):
            ret = 2
        return ret

    # FIXME: This should be moved to a util function somewhere else (like util.py) or moved to the parent class since
    # it will always be used to process range user-supplied parameter.
    @staticmethod
    def _get_range(data):
        """Get the lower and upper bounds of the range.

        :param object data: Data to convert to a range. Could be int, str or list.

        :return: Tuple of (start, end).
        :rtype: tuple
        """
        new_range = []
        if isinstance(data, int):
            new_range = [data]
        elif isinstance(data, str):
            # Could be '0-2000' or '0x0 - 0x700', where in the second case the range is specified in hexa.
            new_range = range(*[int(boundary, 0) for boundary in map(str.strip, data.split('-'))])
        elif isinstance(data, list):
            new_range = data
        return new_range

    def do_start(self, args):
        self.queue_messages = []
        self.last = time.process_time()

        data = [0, 0, 0, 0, 0, 0, 0, 0]
        if 'body' in args:
            data = list(bytes.fromhex(args['body']))

        iso_mode = self._get_iso_mode(args)

        padding = args.get('padding', None)
        shift = int(args.get('shift', 0x8))

        if 'range' not in args:
            self.dprint(1, "No range specified")
            self._active = False
            self.set_error_text("ERROR: No range specified")
            return
        start, end = args.get('range', [0, 0])
        for i in range(int(start), int(end)):
            if iso_mode == 1:
                iso_list = ISOTPMessage.generate_can(i, data, padding)
                iso_list.reverse()
                self.queue_messages.extend(iso_list)
            elif iso_mode == 0:
                self.queue_messages.append(CANMessage.init_data(i, len(data), data[:8]))
            elif iso_mode == 2:
                for service in args.get('services', []):
                    uds_m = UDSMessage(shift, padding)
                    for service_id in self._get_range(service['service']):
                        # https://github.com/eik00d/CANToolz/issues/93 by @DePierre
                        subservice_ids = service.get('sub', None)
                        if subservice_ids is None:
                            subservice_ids = [None]
                        else:
                            subservice_ids = self._get_range(subservice_ids)
                        for subservice_id in subservice_ids:
                            iso_list = uds_m.add_request(i, service_id, subservice_id, service.get('data', []))
                            iso_list.reverse()
                            self.queue_messages.extend(iso_list)
        self._full = len(self.queue_messages)
        self._last = 0

    def do_effect(self, can_msg, args):
        d_time = float(args.get('delay', 0))
        if not can_msg.CANData:
            if d_time > 0:
                if time.process_time() - self.last >= d_time:
                    self.last = time.process_time()
                    can_msg.CANFrame = self.do_ping(args)

                else:
                    can_msg.CANFrame = None
            else:
                can_msg.CANFrame = self.do_ping(args)

            if can_msg.CANFrame and not can_msg.CANData:
                can_msg.CANData = True
                can_msg.bus = self._bus
                self._last += 1
                self._status = self._last / (self._full / 100.0)

        return can_msg
