"""Output a guide to help write your own MWOT from your desired bits."""

from ..util import chunks
from .share import default_dummies


def decomp(bits, cols=8, dummies=default_dummies, no_bit='-', **_):
    """Decompile to a guide for writing MWOT source.

    The guide will itself be valid MWOT.

    Example output for bits 110011111 and cols=6:

        110011  x x zz zz x x
        111---  x x x
    """
    def lines():
        for row in chunks(bits, cols):
            line_bits = ''.join(map(str, row)).ljust(cols, no_bit)
            line_dummies = ' '.join(dummies[i] for i in row)
            yield f'{line_bits}  {line_dummies}\n'
    return ''.join(lines())
