import math
import numpy

from collections import Iterable, deque

from cantoolz.stream.processor import Processor


class Normalizer(Processor):
    def __init__(self, size: int, message_builder: callable):
        self._message_builder = message_builder
        self._size = size
        self._queue = deque()

    def process(self, message) -> Iterable:
        value = float(message)

        if len(self._queue) == self._size:
            self._queue.popleft()

        self._queue.append(value)

        array = numpy.array(self._queue)
        mean = array.mean()
        var = math.sqrt(array.var())

        norm = (value - mean) / var

        if norm == norm:
                yield self._message_builder(
                    message, norm)
