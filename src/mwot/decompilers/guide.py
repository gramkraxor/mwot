"""Output a guide to help write your own MWOT from your desired bits."""

from ..util import chop

dummies = ('zz', 'Z')
no_bit = '.'


def decomp(bits, width=8):
    """Decompile to a guide for writing MWOT source.

    The guide will itself be valid MWOT.

    Example output for bits 01011010 and width 4:

        0101  zz Z zz Z
        1010  Z zz Z zz

    Example output for bits 101 and width 6:

        101...  Z zz Z
    """
    lines = []
    for row in chop(bits, width):
        line_bits = ''.join(map(str, row)).ljust(width, no_bit)
        line_dummies = ' '.join(dummies[i] for i in row)
        line = f'{line_bits}  {line_dummies}\n'
        lines.append(line)
    return ''.join(lines)
