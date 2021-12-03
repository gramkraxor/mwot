"""Analagous functions of `str` and `bytes`.

`mwot` recognizes up to four different string-like types:
    1. `str`
    2. `bytes`
    3. Iterables of single-character `str`s
    4. Iterables of `int`s in `range(256)`
The types are identified in the following ways, respectively:
    1. Instance of `str`
    2. Instance of `bytes`
    3. First item yielded is a `str`
    4. First item yielded is an `int`
"""

import io
import itertools


def ask(s):
    """Ask a string for its type."""
    for t in (Str, Bytes):
        if isinstance(s, t.type):
            return t
    return None


def ask_char(char):
    """Ask a single character for its corresponding string type."""
    for t in (Str, Bytes):
        if isinstance(char, t.chartype):
            return t
    return None


def decode(s):
    """Convert a string to `str`."""
    stype = ask(s)
    if stype is Str:
        return s
    if stype is Bytes:
        return s.decode()
    raise TypeError('cannot decode non-string')


def encode(s):
    """Convert a string to `bytes`."""
    stype = ask(s)
    if stype is Str:
        return s.encode()
    if stype is Bytes:
        return s
    raise TypeError('cannot encode non-string')


def StringIO(s):
    """Create a `StringIO` or `BytesIO` from a string."""
    stype = ask(s)
    if stype is Str:
        return io.StringIO(s)
    if stype is Bytes:
        return io.BytesIO(s)
    raise TypeError('cannot open non-string')


class SType:
    """A bundle of analagous functions for `str` and `bytes`."""

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
        """Convert a single `str` character to this type."""
        return cls._ord(c)


class Str(SType):
    _buffer = lambda textio: textio
    _convert = decode
    _iomode = 't'
    _join = ''.join
    _ord = lambda c: chr(ord(c))
    type = str
    chartype = str


class Bytes(SType):
    _buffer = lambda textio: textio.buffer
    _convert = encode
    _iomode = 'b'
    _join = bytes
    _ord = ord
    type = bytes
    chartype = int


def probe(s, default=Str):
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
        raise TypeError('iterable yields neither bytes nor str characters')
    return stype, itertools.chain((first,), s)
