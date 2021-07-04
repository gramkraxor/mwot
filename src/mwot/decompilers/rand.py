"""Decompile to random gibberish."""

import random
from string import ascii_lowercase

from .share import default_width, wrap_source


def decomp(bits, width=default_width, **_):
    """Decompile to words of random length with random letters."""
    words = map(rand_word, bits)
    unwrapped = ' '.join(words)
    return wrap_source(unwrapped, width=width)


def rand_word(bit):
    """Word of random length with random letters.

    Even/oddness of the length will match `bit`.
    """
    length = random.randrange(2, 13, 2) - bit
    letters = (random.choice(ascii_lowercase) for _ in range(length))
    return ''.join(letters)
