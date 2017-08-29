from collections import Iterable
from itertools import combinations_with_replacement as combinations

from cantoolz.stream.processor import Processor
from cantoolz.stream.sampler import Sampler


class ForcedSampler(Processor):
    def __init__(self, power: int, joiner: callable):
        self._power = power
        self._joiner = joiner
        self._sampler = Sampler(True)
        self._streams = set()

    def process(self, message) -> Iterable:
        stream = str(message)

        if stream not in self._streams:
            self._streams.add(stream)

            for bind in combinations(self._streams, self._power):
                if stream in bind:
                    self._sampler.bind(sorted(bind), self._joiner)

        yield from self._sampler.process(message)

    def flush(self) -> Iterable:
        yield from self._sampler.flush()
