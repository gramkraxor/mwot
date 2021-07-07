"""General functions, etc."""

import itertools

from . import stypes


def chunks(it, size):
    """Chop an iterable into chunks of length `size`.

    Also yields the remainder chunk.
    """
    it = iter(it)
    while chunk := tuple(itertools.islice(it, size)):
        yield chunk


def deshebang(s):
    """Remove a leading shebang line."""
    stype, s = stypes.probe(s)
    shebang = stype.convert('#!')
    newline = stype.ord('\n')
    leading = stype.join(itertools.islice(s, len(shebang)))
    if leading == shebang:
        # Drop the rest of the line.
        for char in s:
            if char == newline:
                break
    else:
        yield from leading
    yield from s


def split(s):
    """Split a `str` string-like on whitespace."""
    s = iter(s)

    def nextword():
        for char in s:
            if not char.isspace():
                yield char
                break
        for char in s:
            if char.isspace():
                break
            yield char

    while word := ''.join(nextword()):
        yield word
