"""Decompile to the simplest possible MWOT."""

from .share import default_dummies, default_width, wrap_words


def decomp(bits, dummies=default_dummies, width=default_width, **_):
    """Translate 0s and 1s to dummies[0] and dummies[1]."""
    words = (dummies[i] for i in bits)
    return wrap_words(words, width=width)
