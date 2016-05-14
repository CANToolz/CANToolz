from collections import Counter, Iterable

from cantoolz.stream.processor import Processor


class Sampler(Processor):
    def __init__(self, stateless: bool = False):
        self._tick = Counter()
        self._state = dict()
        self._joins = dict()
        self._stateless = stateless

    def process(self, message) -> Iterable:
        stream = str(message)

        if self._tick[stream] > 0:
            yield from self.flush()

        self._state[stream] = message
        self._tick[stream] += 1

    def flush(self):
        for bind in self._joins:
            if all(map(self._stream_in_state, bind)):
                yield self._joins[bind](*map(self._stream_state, bind))

        if self._stateless:
            self._state.clear()

        self._tick.clear()

    def bind(self, bind: Iterable, joiner: callable):
        self._joins[tuple(bind)] = joiner

    def _stream_in_state(self, stream):
        return stream in self._state

    def _stream_state(self, stream):
        return self._state[stream]




