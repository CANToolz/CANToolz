from libs.can import *
import collections

'''
Custom fragmented packets
'''


class FragmentedCAN:

    def __init__(self):  # Init EMPTY message
        self.messages = []
        self.temp_msg = collections.OrderedDict()
        self.temp_msg2 = collections.OrderedDict()

    @staticmethod
    def get_value(in_array):
        in_idx = 0
        for byte in in_array:
            in_idx <<= 8
            in_idx += byte
        return in_idx

    def clean_build_loop(self):
        for fid, body in self.temp_msg.iteritems():  # LOOP detection
            if body['elements'] > 1:
                p_x = -1
                message = collections.OrderedDict()
                for idx in sorted(body['idx'].keys()):
                    if p_x == -1:
                        p_x = idx
                        message['id'] = fid
                        message['message_length'] = body['length']
                        message['message_data'] = []
                    if p_x == idx:
                        message['message_data'] += body['idx'][idx]
                        p_x += 1
                    else:
                        p_x = -1
                        break
                if p_x > 0:
                    self.messages.append(message)

    def clean_build_meta(self):
        for fid, body in self.temp_msg2.iteritems():  # known META print
            if body['elements'] > 1:
                self.messages.append(collections.OrderedDict())
                self.messages[-1]['message_data'] = [] + body['data']
                self.messages[-1]['message_length'] = body['length']
                self.messages[-1]['id'] = fid

    def add_can_meta(self, can_msg, idx1, idx2, strt):  # Add with known META
        if can_msg.frame_length > 0:
            if can_msg.frame_id not in self.temp_msg2:
                self.temp_msg2[can_msg.frame_id] = collections.OrderedDict()
                self.temp_msg2[can_msg.frame_id]['curr_idx'] = strt
                self.temp_msg2[can_msg.frame_id]['index_size'] = idx2 - idx1
                self.temp_msg2[can_msg.frame_id]['data'] = []
                self.temp_msg2[can_msg.frame_id]['length'] = 0
                self.temp_msg2[can_msg.frame_id]['elements'] = 0

            # First frame
            if self.get_value(can_msg.frame_data[idx1:idx2]) == self.temp_msg2[can_msg.frame_id]['curr_idx']:
                self.temp_msg2[can_msg.frame_id]['data'] += can_msg.frame_data[0:idx1] + can_msg.frame_data[idx2:]
                self.temp_msg2[can_msg.frame_id]['length'] += can_msg.frame_length - len(can_msg.frame_data[idx1:idx2])
                self.temp_msg2[can_msg.frame_id]['curr_idx'] += 1
                self.temp_msg2[can_msg.frame_id]['elements'] += 1
            elif self.get_value(can_msg.frame_data[idx1:idx2]) == strt: # New block
                if self.temp_msg2[can_msg.frame_id]['elements'] > 1:
                    self.messages.append(collections.OrderedDict())
                    self.messages[-1]['message_data'] = [] + self.temp_msg2[can_msg.frame_id]['data']
                    self.messages[-1]['message_length'] = self.temp_msg2[can_msg.frame_id]['length']
                    self.messages[-1]['id'] = can_msg.frame_id
                self.temp_msg2[can_msg.frame_id] = collections.OrderedDict()
                self.temp_msg2[can_msg.frame_id]['curr_idx'] = strt
                self.temp_msg2[can_msg.frame_id]['data'] = [] + can_msg.frame_data[0:idx1] + can_msg.frame_data[idx2:]
                self.temp_msg2[can_msg.frame_id]['length'] = can_msg.frame_length - len(can_msg.frame_data[idx1:idx2])
                self.temp_msg2[can_msg.frame_id]['elements'] = 1
            else:
                if self.temp_msg2[can_msg.frame_id]['elements'] > 1:
                    self.messages.append(collections.OrderedDict())
                    self.messages[-1]['message_data'] = [] + self.temp_msg2[can_msg.frame_id]['data']
                    self.messages[-1]['message_length'] = self.temp_msg2[can_msg.frame_id]['length']
                    self.messages[-1]['id'] = can_msg.frame_id
                self.temp_msg2[can_msg.frame_id]['curr_idx'] = strt
                self.temp_msg2[can_msg.frame_id]['data'] = []
                self.temp_msg2[can_msg.frame_id]['length'] = 0
                self.temp_msg2[can_msg.frame_id]['elements'] = 0

    def add_can_loop(self, can_msg):  # Check if there is INDEX byte in first byte
        if can_msg.frame_length > 0:
            if can_msg.frame_id not in self.temp_msg:
                self.temp_msg[can_msg.frame_id] = collections.OrderedDict()
                self.temp_msg[can_msg.frame_id]['idx'] = {}
                self.temp_msg[can_msg.frame_id]['length'] = 0
                self.temp_msg[can_msg.frame_id]['elements'] = 0

            curr_elems = self.temp_msg[can_msg.frame_id]["elements"]
            in_idx = can_msg.frame_data[0]

            if curr_elems == 0 and not self.temp_msg[can_msg.frame_id]['elements'] < 0:
                self.temp_msg[can_msg.frame_id]["elements"] += 1
                self.temp_msg[can_msg.frame_id]["idx"][in_idx] = can_msg.frame_data[1:]
                self.temp_msg[can_msg.frame_id]['length'] += len(can_msg.frame_data[1:])
            elif in_idx in self.temp_msg[can_msg.frame_id]['idx'].keys() and not self.temp_msg[can_msg.frame_id]['elements'] < 0:
                self.temp_msg[can_msg.frame_id]["elements"] = -1
            elif not self.temp_msg[can_msg.frame_id]['elements'] < 0:
                self.temp_msg[can_msg.frame_id]["elements"] += 1
                self.temp_msg[can_msg.frame_id]["idx"][in_idx] = can_msg.frame_data[1:]
                self.temp_msg[can_msg.frame_id]['length'] += len(can_msg.frame_data[1:])




