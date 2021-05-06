"""Output a guide to help write your own MWOT from your desired bits."""

from ..util import chop


def decomp(bits, cols=8, dummies=('zz', 'q'), no_bit='.'):
    """Decompile to a guide for writing MWOT source.

    The guide will itself be valid MWOT.

    Example output for bits 110011111 and cols=6:

        110011  q q zz zz q q
        111...  q q q
    """
    def lines():
        for row in chop(bits, cols):
            line_bits = ''.join(map(str, row)).ljust(cols, no_bit)
            line_dummies = ' '.join(dummies[i] for i in row)
            yield f'{line_bits}  {line_dummies}\n'
    return ''.join(lines())
