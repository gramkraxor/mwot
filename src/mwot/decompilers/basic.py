"""Decompile to the simplest possible MWOT."""

from ..util import wrap_source


def decomp(bits, dummies=('zz', 'q'), width=80):
    """Translate 0s and 1s to dummies[0] and dummies[1]."""
    words = (dummies[i] for i in bits)
    unwrapped = ' '.join(words)
    return wrap_source(unwrapped, width=width)
