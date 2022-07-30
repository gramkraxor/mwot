"""Analagous functions of text and byte strings.

Up to four different string-like types are recognized:
    1. Text strings
    2. Byte strings
    3. Text iterables
    4. Byte iterables
The types are identified in the following ways, respectively:
    1. Instance of `str`
    2. Instance of `bytes` or `bytearray`
    3. First item yielded is a single-character `str`
    4. First item yielded is an `int` in `range(256)`
"""

import io
import itertools


def ask(s):
    """Ask a string for its type."""
    for t in (Text, Bytes):
        if t.ask(s):
            return t
    return None


def ask_char(char):
    """Ask a single character for its corresponding string type."""
    for t in (Text, Bytes):
        if t.ask_char(char):
            return t
    return None


def decode(s):
    """Convert a string to text."""
    stype = ask(s)
    if stype is Text:
        return s
    if stype is Bytes:
        return s.decode()
    raise TypeError('cannot decode non-string')


def encode(s):
    """Convert a string to bytes."""
    stype = ask(s)
    if stype is Text:
        return s.encode()
    if stype is Bytes:
        return s
    raise TypeError('cannot encode non-string')


def StringIO(s):
    """Create an I/O object from a string."""
    stype = ask(s)
    if stype is Text:
        return io.StringIO(s)
    if stype is Bytes:
        return io.BytesIO(s)
    raise TypeError('cannot open non-string')


class SType:
    """A bundle of analagous functions for text and byte strings."""

    @classmethod
    def ask(cls, s):
        """Ask a string if it is this type."""
        return cls._ask(s)

    @classmethod
    def ask_char(cls, c):
        """Ask a character if it corresponds to this type."""
        return cls._ask_char(c)

    @classmethod
    def buffer(cls, textio):
        """Return `textio` or its buffer."""
        return cls._buffer(textio)

    @classmethod
    def convert(cls, s):
        """Convert a string to this type."""
        return cls._convert(s)

    @classmethod
    def iomode(cls, mode):
        """Add a 't' or 'b' to the end of `mode`."""
        return f'{mode}{cls._iomode}'

    @classmethod
    def join(cls, s):
        """Join an iterable of characters."""
        return cls._join(s)

    @classmethod
    def ord(cls, c):
        """Convert a single text character to this type."""
        return cls._ord(c)


class Text(SType):
    """Unicode strings."""

    _ask = lambda s: isinstance(s, str)
    _ask_char = lambda c: isinstance(c, str) and len(c) == 1
    _buffer = lambda textio: textio
    _convert = decode
    _iomode = 't'
    _join = ''.join
    _ord = lambda c: chr(ord(c))


class Bytes(SType):
    """Byte strings."""

    _ask = lambda s: isinstance(s, (bytes, bytearray))
    _ask_char = lambda c: isinstance(c, int) and c in range(256)
    _buffer = lambda textio: textio.buffer
    _convert = encode
    _iomode = 'b'
    _join = bytes
    _ord = ord


def probe(s, default=Text):
    """Probe a string-like for its type with `next(iter(s))`.

    Returns (`stype`, `s2`). The returned `s2` should replace `s`, since
    `s` will be partially exhausted.

    If `s` yields nothing, the returned `stype` will be `default`.
    """
    s = iter(s)
    try:
        first = next(s)
    except StopIteration:
        return default, itertools.chain(())
    stype = ask_char(first)
    if stype is None:
        raise TypeError('iterable yields neither bytes nor text characters')
    return stype, itertools.chain((first,), s)
