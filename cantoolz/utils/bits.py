import math


def xor(a: bytes, b: bytes, l: int) -> bytes:
    result = bytearray(l)

    for i in range(l):
        result[i] = a[i] ^ b[i]

    return bytes(result)


def test(frame: bytes, offset: int) -> bool:
    byte = frame[offset // 8]
    mask = 1 << (7 - offset % 8)

    return byte & mask > 0


def align(frame: bytes, size: int, align: int) -> bytes:
    result = bytearray(align)

    for i in range(align):
        if align - i - 1 < size:
            result[i] = frame[align - i - 1]

    return bytes(result)


# assert slice_int(struct.pack('!I',
#   int('11110111111111111111111111111111', 2)), 0, 8) == int('11110111', 2)
def read_int(frame: bytes, offset: int, limit: int) -> int:
    result = 0
    size = len(frame)

    for i, x in enumerate(range(offset + limit, offset, -8)):
        l = x // 8
        h = l - 1
        bit = x % 8

        if l < size:
            byte = frame[h] << bit & 255 | frame[l] >> 8 - bit
        else:
            byte = frame[h] << bit & 255

        if x - 8 < offset:
            byte &= 255 >> offset - x + 8

        result |= byte << 8 * i

    return result


def read(frame: bytes, offset: int, limit: int) -> (int, bytes):
    frame_size = len(frame)
    result_size = math.ceil(limit / 8)
    result = bytearray(result_size)

    for i, x in enumerate(range(offset + limit, offset, -8)):
        l = x // 8
        h = l - 1
        bit = x % 8

        if l < frame_size:
            byte = frame[h] << bit & 255 | frame[l] >> 8 - bit
        else:
            byte = frame[h] << bit & 255

        if x - 8 < offset:
            byte &= 255 >> offset - x + 8

        result[result_size - i - 1] = byte

    return result_size, bytes(result)
