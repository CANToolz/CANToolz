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

    def clean_build(self):
        for fid, body in self.temp_msg.iteritems():
            if body['curr_idx'] != -1:
                self.messages.append(collections.OrderedDict())
                self.messages[-1]['message_data'] = [] + body['data']
                self.messages[-1]['message_length'] = body['length']
                self.messages[-1]['id'] = fid
        for fid, body in self.temp_msg2.iteritems():
            if body['curr_idx'] != -1:
                self.messages.append(collections.OrderedDict())
                self.messages[-1]['message_data'] = [] + body['data']
                self.messages[-1]['message_length'] = body['length']
                self.messages[-1]['id'] = fid

    def add_can_meta(self, can_msg, idx1, idx2, strt):  # Add with known META
        if can_msg.frame_id not in self.temp_msg2:
            self.temp_msg2[can_msg.frame_id] = collections.OrderedDict()
            self.temp_msg2[can_msg.frame_id]['curr_idx'] = strt
            self.temp_msg2[can_msg.frame_id]['index_size'] = idx2 - idx1
            self.temp_msg2[can_msg.frame_id]['data'] = []
            self.temp_msg2[can_msg.frame_id]['length'] = 0

        if self.get_value(can_msg.frame_data[idx1:idx2]) == self.temp_msg2[can_msg.frame_id]['curr_idx']:
            self.temp_msg2[can_msg.frame_id]['data'] += can_msg.frame_data[0:idx1] + can_msg.frame_data[idx2:]
            self.temp_msg2[can_msg.frame_id]['length'] += can_msg.frame_length - len(can_msg.frame_data[idx1:idx2])
            self.temp_msg2[can_msg.frame_id]['curr_idx'] += 1
        elif self.get_value(can_msg.frame_data[idx1:idx2]) == strt: # New block
            self.messages.append(collections.OrderedDict())
            self.messages[-1]['message_data'] = [] + self.temp_msg2[can_msg.frame_id]['data']
            self.messages[-1]['message_length'] = self.temp_msg2[can_msg.frame_id]['length']
            self.messages[-1]['id'] = can_msg.frame_id
            self.temp_msg2[can_msg.frame_id] = collections.OrderedDict()
            self.temp_msg2[can_msg.frame_id]['curr_idx'] = strt
            self.temp_msg2[can_msg.frame_id]['index_size'] = idx2 - idx1
            self.temp_msg2[can_msg.frame_id]['data'] = [] + can_msg.frame_data[0:idx1] + can_msg.frame_data[idx2:]
            self.temp_msg2[can_msg.frame_id]['length'] = 0

    def add_can(self, can_msg):  # Check if there is INDEX byte in first byte
        if can_msg.frame_id not in self.temp_msg:
            self.temp_msg[can_msg.frame_id] = collections.OrderedDict()
            self.temp_msg[can_msg.frame_id]['curr_idx'] = -1
            self.temp_msg[can_msg.frame_id]['index_size'] = 0
            self.temp_msg[can_msg.frame_id]['data'] = []
            self.temp_msg[can_msg.frame_id]['length'] = 0
            self.temp_msg[can_msg.frame_id]['init'] = []

        curr_idx = self.temp_msg[can_msg.frame_id].get("curr_idx", -1)
        curr_size = self.temp_msg[can_msg.frame_id].get("index_size", 0)
        in_idx = self.get_value(can_msg.frame_data[0:curr_size])

        if curr_idx != -1 and curr_idx == in_idx:
            self.temp_msg[can_msg.frame_id]['curr_idx'] += 1
            self.temp_msg[can_msg.frame_id]['data'] += can_msg.frame_data[curr_size:]
            self.temp_msg[can_msg.frame_id]['length'] += can_msg.frame_length - curr_size
        elif curr_idx == -1 and in_idx == 0 and curr_size == 0 and len(self.temp_msg[can_msg.frame_id]['init']) == 0:
            self.temp_msg[can_msg.frame_id]['init'] = can_msg.frame_data
        elif curr_idx == -1 and in_idx == 0 and curr_size == 0 and len(self.temp_msg[can_msg.frame_id]['init']) > 1:
            if self.temp_msg[can_msg.frame_id]['init'][0]+1 == can_msg.frame_data[0]:
                self.temp_msg[can_msg.frame_id]['curr_idx'] = can_msg.frame_data[0]
                self.temp_msg[can_msg.frame_id]['index_size'] = 1
                self.temp_msg[can_msg.frame_id]['data'] = self.temp_msg[can_msg.frame_id]['init'][1:] + can_msg.frame_data[1:]
                self.temp_msg[can_msg.frame_id]['length'] = can_msg.frame_length - 1 + len(self.temp_msg[can_msg.frame_id]['init'][1:])
            elif self.get_value(self.temp_msg[can_msg.frame_id]['init'][0:2]) + 1 == self.get_value(can_msg.frame_data[0:2]):
                self.temp_msg[can_msg.frame_id]['curr_idx'] = self.get_value(can_msg.frame_data[0:2])
                self.temp_msg[can_msg.frame_id]['index_size'] = 2
                self.temp_msg[can_msg.frame_id]['data'] = self.temp_msg[can_msg.frame_id]['init'][2:] + can_msg.frame_data[2:]
                self.temp_msg[can_msg.frame_id]['length'] = can_msg.frame_length - 2 + len(self.temp_msg[can_msg.frame_id]['init'][2:])
            else:
                self.temp_msg[can_msg.frame_id]['init'] = can_msg.frame_data
        elif curr_idx != -1 and curr_idx != in_idx:
            self.messages.append(collections.OrderedDict())
            self.messages[-1]['message_data'] = [] + self.temp_msg[can_msg.frame_id]['data']
            self.messages[-1]['message_length'] = self.temp_msg[can_msg.frame_id]['length']
            self.messages[-1]['id'] = can_msg.frame_id
            self.temp_msg[can_msg.frame_id]['init'] = can_msg.frame_data
            self.temp_msg[can_msg.frame_id]['curr_idx'] = -1
            self.temp_msg[can_msg.frame_id]['index_size'] = 0
            self.temp_msg[can_msg.frame_id]['data'] = []
            self.temp_msg[can_msg.frame_id]['length'] = 0
