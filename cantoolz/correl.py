from collections import deque
from sys import stdin
from struct import unpack

from cantoolz.utils import bits
from cantoolz.stream.normalizer import Normalizer
from cantoolz.stream.processor import Processor
from cantoolz.stream.subnet import Subnet
from cantoolz.stream.selector import Selector
from cantoolz.stream.integrator import Integrator
from cantoolz.stream.forced_sampler import ForcedSampler
from cantoolz.stream.separator import Separator


class RawMessage:
    def __init__(self, fid, size, data):
        self._stream = int(fid)
        self._size = int(size)
        self._payload = bytes(data)


class SeparatedMessage:

    @classmethod
    def builder(cls, raw, index, payload, size):
        return cls(str(raw) + '|' + str(index),
                   unpack('!I', bits.align(payload, size, 4))[0])

    def __init__(self, stream, value):
        self._stream = stream
        self._value = value

    def __float__(self):
        return float(self._value)

    def __str__(self):
        return self._stream


class FloatMessage:
    @classmethod
    def conv(cls, a, b):
        return cls(str(a) + '*' + str(b), float(a) * float(b))

    @classmethod
    def simple(cls, raw, value):
        return cls(str(raw), value)

    def __init__(self, stream, value):
        self._stream = stream
        self._value = value

    def __float__(self):
        return self._value

    def __str__(self):
        return self._stream


def same(x):
    return x
