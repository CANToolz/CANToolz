from collections import Counter, Iterable

from cantoolz.stream.processor import Processor


class Subnet(Processor):
    def __init__(self, device_builder: callable):
        self._devices = dict()
        self._device_builder = device_builder

    def process(self, message) -> Iterable:
        stream = str(message) + ":" + str(len(message))
        if stream not in self._devices:
            self._devices[stream] = self._device_builder(stream)

        yield from self._devices[stream].process(message)