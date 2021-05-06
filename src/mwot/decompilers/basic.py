"""Decompile to the simplest possible MWOT."""

from ..util import default_width, wrap_source
from .share import default_dummies


def decomp(bits, dummies=default_dummies, width=default_width):
    """Translate 0s and 1s to dummies[0] and dummies[1]."""
    words = (dummies[i] for i in bits)
    unwrapped = ' '.join(words)
    return wrap_source(unwrapped, width=width)
