"""Decompile to the simplest possible MWOT."""

from ..util import default_width, wrap_source


def decomp(bits, dummies=('zz', 'q'), width=default_width):
    """Translate 0s and 1s to dummies[0] and dummies[1]."""
    words = (dummies[i] for i in bits)
    unwrapped = ' '.join(words)
    return wrap_source(unwrapped, width=width)
