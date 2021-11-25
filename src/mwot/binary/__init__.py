"""Binary (bytes) language: conversions between bytes and MWOT bits."""

import itertools
import warnings

from ..join import joinable
from ..util import chunks

bitrange = range(8)[::-1]


@joinable(bytes)
def from_bits(bits):
    """Yield bytes from MWOT bits."""
    chunk_size = 8
    for chunk in chunks(bits, chunk_size):
        if len(chunk) < chunk_size:
            chunk += (0,) * (chunk_size - len(chunk))
            message = (f'word count not divisible by {chunk_size}; trailing '
                       f'zero(s) added')
            warnings.warn(message, RuntimeWarning)
        yield sum(b << i for i, b in zip(bitrange, chunk))


@joinable()
def to_bits(chars):
    """Convert a string of brainfuck to a chain of MWOT bits."""
    for byte in chars:
        for i in bitrange:
            yield (byte >> i) & 1
