"""General functions, etc."""

import itertools
import textwrap

ascii_range = range(128)
byte_range = range(256)


def chop(it, size):
    """Chop an iterable into chunks of length ``size``.

    Also yields the remainder chunk.
    """
    it = iter(it)
    while chunk := tuple(itertools.islice(it, size)):
        yield chunk


def decode(chars, ensure=True):
    """Convert an iterable of ints or strs into a str iterable."""
    if isinstance(chars, str):
        return chars
    if isinstance(chars, bytes):
        return chars.decode('ascii', errors='ignore')
    strtype, chars = probe_strtype(chars)
    if strtype is str:
        return ensure_str(chars) if ensure else chars
    if ensure:
        chars = ensure_bytes(chars)
    return (chr(c) for c in chars if c in ascii_range)


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


def ensure_bytes(chars):
    """Make sure every item in the iterable is a byte."""
    for char in chars:
        if not isinstance(char, int) or char not in byte_range:
            raise TypeError('iterable does not exclusively yield bytes')
        yield char


def ensure_str(chars):
    """Make sure every item in the iterable is a str character."""
    for char in chars:
        if not isinstance(char, str) or len(char) != 1:
            raise TypeError('iterable does not exclusively yield str '
                            'characters')
        yield char


def probe_strtype(chars):
    """Probe a string iterable for its type.

    Checks whether the first item is an int or a str, corresponding to
    bytes and str, respectively.

    Returns (strtype, chars). The returned chars should replace the old
    chars, since the old chars will be partially exhausted.
    """
    chars = iter(chars)
    try:
        first = next(chars)
    except StopIteration:
        # Consider an empty iterable a str.
        return str, iter(())
    if isinstance(first, str):
        strtype = str
    elif isinstance(first, int):
        strtype = bytes
    else:
        raise TypeError('iterable yields neither bytes nor str characters')
    return strtype, itertools.chain((first,), chars)


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


def wrap_source(text, width=80):
    """Wrapping algorithm suitable for MWOT source."""
    lines = textwrap.wrap(text, width=width, break_long_words=False,
                          break_on_hyphens=False)
    return '\n'.join((*lines, ''))
