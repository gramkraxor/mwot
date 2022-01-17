"""Output a guide to help write your own MWOT from your desired bits."""

from ..join import joinable
from ..util import chunks
from .common import default_vocab


@joinable(str)
def decomp(bits, cols=8, vocab=default_vocab, no_bit='-', **_):
    """Decompile to a guide for writing MWOT source.

    The guide will itself be valid MWOT.

    Example output for bits 110011111 and cols=6:

        110011  n n mm mm n n
        111---  n n n
    """
    for row in chunks(bits, cols):
        line_bits = ''.join(map(str, row)).ljust(cols, no_bit)
        line_words = ' '.join(vocab[i] for i in row)
        yield f'{line_bits}  {line_words}\n'
