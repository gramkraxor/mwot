"""Binary (bytes) language: conversions between bytes and MWOT bits."""

import itertools
from ..exceptions import CompilerError
from ..util import chop, collectable

bitrange = range(8)[::-1]


@collectable(bytes)
def from_bits(bits):
    """Yield bytes from MWOT bits."""
    chunk_size = 8
    for chunk in chop(bits, chunk_size):
        if len(chunk) != chunk_size:
            raise CompilerError(f'word count not divisible by {chunk_size}')
        yield sum(b << i for i, b in zip(bitrange, chunk))


@collectable()
def to_bits(chars):
    """Convert a string of brainfuck to a chain of MWOT bits."""
    for byte in chars:
        for i in bitrange:
            yield (byte >> i) & 1
