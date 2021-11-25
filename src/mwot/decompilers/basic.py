"""Decompile to the simplest possible MWOT."""

from .common import default_vocab, default_width, wrap_words


def decomp(bits, vocab=default_vocab, width=default_width, **_):
    """Translate 0s and 1s to vocab[0] and vocab[1]."""
    words = (vocab[i] for i in bits)
    return wrap_words(words, width=width)
