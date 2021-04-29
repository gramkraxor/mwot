"""Turn MWOT into bits."""

from .util import collectable, deshebang, split


@collectable()
def bits_from_mwot(mwot):
    """Yield MWOT bits from MWOT source.

    Yields the even/oddness of the letter count of each whitespace-
    separated word, ignoring words with 0 letters.
    """
    for word in split(deshebang(mwot)):
        length = letter_count(word)
        if length:
            yield length & 1


def letter_count(word):
    """How many charaters in ``word`` satisfy ``str.isalpha()``?"""
    return sum(map(str.isalpha, word))
