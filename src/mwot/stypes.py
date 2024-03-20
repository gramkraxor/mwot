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
    for t in (TEXT, BYTES):
        if t.ask(s):
            return t
    return None


def ask_char(char):
    """Ask a single character for its corresponding string type."""
    for t in (TEXT, BYTES):
        if t.ask_char(char):
            return t
    return None


def decode(s):
    """Convert a string to text."""
    stype = ask(s)
    if stype is TEXT:
        return s
    if stype is BYTES:
        return s.decode()
    raise TypeError('cannot decode non-string')


def encode(s):
    """Convert a string to bytes."""
    stype = ask(s)
    if stype is TEXT:
        return s.encode()
    if stype is BYTES:
        return s
    raise TypeError('cannot encode non-string')


def StringIO(s):
    """Create an I/O object from a string."""
    stype = ask(s)
    if stype is TEXT:
        return io.StringIO(s)
    if stype is BYTES:
        return io.BytesIO(s)
    raise TypeError('cannot open non-string')


class SType:
    """A bundle of analagous functions for text and byte strings."""

    def __init__(
        self,
        ask_fn,
        ask_char_fn,
        buffer_fn,
        convert_fn,
        iomode,
        join_fn,
        ord_fn,
    ):
        self._ask = ask_fn
        self._ask_char = ask_char_fn
        self._buffer = buffer_fn
        self._convert = convert_fn
        self._iomode = iomode
        self._join = join_fn
        self._ord = ord_fn

    def ask(self, s):
        """Ask a string if it is this type."""
        return self._ask(s)

    def ask_char(self, c):
        """Ask a character if it corresponds to this type."""
        return self._ask_char(c)

    def buffer(self, textio):
        """Return `textio` or its buffer."""
        return self._buffer(textio)

    def convert(self, s):
        """Convert a string to this type."""
        return self._convert(s)

    def iomode(self, mode):
        """Add a 't' or 'b' to the end of `mode`."""
        return f'{mode}{self._iomode}'

    def join(self, s):
        """Join an iterable of characters."""
        return self._join(s)

    def ord(self, c):
        """Convert a single text character to this type."""
        return self._ord(c)


# Unicode strings
TEXT = SType(
    ask_fn=lambda s: isinstance(s, str),
    ask_char_fn=lambda c: isinstance(c, str) and len(c) == 1,
    buffer_fn=lambda textio: textio,
    convert_fn=decode,
    iomode='t',
    join_fn=''.join,
    ord_fn=lambda c: chr(ord(c)),
)
# Byte strings
BYTES = SType(
    ask_fn=lambda s: isinstance(s, (bytes, bytearray)),
    ask_char_fn=lambda c: isinstance(c, int) and c in range(256),
    buffer_fn=lambda textio: textio.buffer,
    convert_fn=encode,
    iomode='b',
    join_fn=bytes,
    ord_fn=ord,
)


def probe(s, default=TEXT):
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
