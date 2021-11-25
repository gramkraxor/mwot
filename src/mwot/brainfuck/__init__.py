"""Brainfuck language: conversions between brainfuck and MWOT bits.

Instructions are mapped to bits in the following order:
    >   000
    <   001
    +   010
    -   011
    .   100
    ,   101
    [   110
    ]   111
"""

import itertools
import warnings

from ..join import joinable
from ..util import chunks

cmds = b'><+-.,[]'
allchunks = tuple(itertools.product((0, 1), repeat=3))  # 000 001 ...
cmdmap = dict(zip(allchunks, cmds))
chunkmap = dict(zip(cmds, allchunks))
hello_world = (b'++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.++++'
               b'+++..+++.>>.<-.<.+++.------.--------.>>+.>++.')


@joinable(bytes)
def from_bits(bits):
    """Yield brainfuck instructions from MWOT bits."""
    chunk_size = 3
    for chunk in chunks(bits, chunk_size):
        if len(chunk) < chunk_size:
            chunk += (0,) * (chunk_size - len(chunk))
            message = (f'word count not divisible by {chunk_size}; trailing '
                       f'zero(s) added')
            warnings.warn(message, RuntimeWarning)
        yield cmdmap[chunk]


@joinable()
def to_bits(chars):
    """Convert a string of brainfuck to a chain of MWOT bits."""
    for cmd in chars:
        yield from chunkmap.get(cmd, ())


from . import interpreter
