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

from ..join import joinable
from .. import stypes
from ..util import chunk_bits

cmds = b'><+-.,[]'
allchunks = tuple(itertools.product((0, 1), repeat=3))  # 000 001 ...
cmdmap = dict(zip(allchunks, cmds))
chunkmap = dict(zip(cmds, allchunks))
hello_world = (b'++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.++++'
               b'+++..+++.>>.<-.<.+++.------.--------.>>+.>++.')


@joinable(bytes)
def from_bits(bits):
    """Yield brainfuck instructions from MWOT bits."""
    for chunk in chunk_bits(bits, chunk_size=3):
        yield cmdmap[chunk]


@joinable()
def to_bits(chars):
    """Convert brainfuck to MWOT bits."""
    stype, chars = stypes.probe(chars)
    if stype is not stypes.Bytes:
        raise TypeError('chars must yield bytes')
    for cmd in chars:
        yield from chunkmap.get(cmd, ())


from . import interpreter
