from collections import Iterable


class Processor:
    def process(self, message) -> Iterable:
        pass

    def flush(self) -> Iterable:
        yield from ()

    def __mul__(self, other):
        return _Composition(self, other)

    def __call__(self, source: Iterable = None) -> Iterable:
        if source is not None:
            for message in source:
                yield from self.process(message)
        else:
            yield from self.flush()


class _Composition(Processor):
    def __init__(self, source: Processor, target: Processor):
        self._source = source
        self._target = target

    def process(self, message) -> Iterable:
        yield from self._target(self._source.process(message))
