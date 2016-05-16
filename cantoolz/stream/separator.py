from collections import Counter, deque, Iterable

from cantoolz.stream.processor import Processor
from cantoolz.utils import bits
from cantoolz.utils import stats


class Separator(Processor):
    def __init__(self, message_builder: callable):
        self._message_builder = message_builder
        self._distribution = Counter()
        self._state = None

    def process(self, message) -> Iterable:
        msg_size = len(message)

        if self._state is not None:
            self._count_bits(bits.xor(
                bytes(message), bytes(self._state), msg_size), msg_size)

        self._state = message

        start = 0

        for i, end in enumerate(self._indexes()):
            size, payload = bits.read(bytes(self._state), start, end - start)

            yield self._message_builder(
                message, i, payload, size)

            start = end

    def _count_bits(self, frame: bytes, size: int):
        for i in range(8 * size):
            if bits.test(frame, i):
                self._distribution[i] += 1

    def _gaps(self) -> iter:
        gaps = deque()
        prev = None

        for x in range(len(self._state) * 8, 0, -1):
            curr = self._distribution[x - 1]

            if prev is not None:
                if prev < curr:
                    gaps.appendleft(curr - prev)
                else:
                    gaps.appendleft(0)

            prev = curr

        return gaps

    def _indexes(self) -> iter:
        indexes = list()
        gaps = self._gaps()
        edge = stats.max_dx_edge(gaps)

        for i, x in enumerate(gaps):
            if x > edge:
                indexes.append(i + 1)

        indexes.append(len(self._state) * 8)

        return indexes