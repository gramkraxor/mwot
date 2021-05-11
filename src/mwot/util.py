"""General functions, etc."""

from functools import wraps
import itertools

ascii_range = range(128)
byte_range = range(256)


def chunks(it, size):
    """Chop an iterable into chunks of length `size`.

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


class Joinable:
    """Wrapper for an iterator that can be joined easily."""

    # Collector functions that aren't their type constructors
    _collectors = {
        None: list,
        str: ''.join,
    }

    def __init__(self, iterator, seq_type=None, function=None):
        self.iterator = iterator
        self.seq_type = seq_type
        self.collect = self._collectors.get(seq_type, seq_type)
        self.function = function

    def __iter__(self):
        return self

    def __next__(self):
        return self.iterator.__next__()

    def __repr__(self):
        infos = ['joinable']
        if self.seq_type is not None:
            infos.append(self.seq_type.__qualname__)
        if self.function is not None:
            module = self.function.__module__
            func = self.function.__qualname__
            infos.append(f'{module}.{func}')
        info = ' '.join(infos)
        return f'<{info}>'

    def join(self):
        """Return self, joined with the correct collector."""
        return self.collect(self.iterator)


def joinable(seq_type=None):
    """Decorator for iterable functions to add a collect option.

    `Joinable`'s `join()` interface unifies the joining functions for
    various types: `''.join()`, `bytes()`, `list()`.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            iterator = f(*args, **kwargs)
            return Joinable(iterator, seq_type, function=f)
        return wrapper
    return decorator


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
