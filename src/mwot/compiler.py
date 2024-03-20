"""Turn MWOT into bits."""

from .join import joinable
from . import stypes
from .util import deshebang, split


@joinable()
def bits_from_mwot(mwot):
    """Yield MWOT bits from MWOT source.

    Yields the even/oddness of the letter count of each
    whitespace-separated word, ignoring words with 0 letters.
    """
    stype, mwot = stypes.probe(mwot, default=stypes.TEXT)
    if stype is not stypes.TEXT:
        raise TypeError('mwot must be text')
    for word in split(deshebang(mwot, stype)):
        length = letter_count(word)
        if length:
            yield length & 1


def letter_count(word):
    """How many charaters in `word` satisfy `str.isalpha()`?"""
    return sum(map(str.isalpha, word))
