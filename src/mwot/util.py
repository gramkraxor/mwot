"""General functions, etc."""

import itertools


def deshebang(chars, strtype=str):
    """Remove a leading shebang line."""
    if strtype is str:
        shebang = '#!'
        newline = '\n'
        join = ''.join
    elif strtype is bytes:
        shebang = b'#!'
        newline = ord('\n')
        join = bytes
    else:
        raise TypeError('strtype must be str or bytes')
    chars = iter(chars)
    leading = join(itertools.islice(chars, len(shebang)))
    if leading == shebang:
        # Drop the rest of the line.
        for char in chars:
            if char == newline:
                break
    else:
        yield from leading
    yield from chars


def split(chars):
    """Split a string/iterable on whitespace."""
    chars = iter(chars)

    def nextword():
        for char in chars:
            if not char.isspace():
                yield char
                break
        for char in chars:
            if char.isspace():
                break
            yield char

    while word := ''.join(nextword()):
        yield word
