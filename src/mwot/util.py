"""General functions, etc."""

from collections import deque
import itertools
import warnings

from . import stypes


def chunks(it, size):
    """Chop an iterable into chunks of length `size`.

    Also yields the remainder chunk.
    """
    it = iter(it)
    while chunk := tuple(itertools.islice(it, size)):
        yield chunk


def chunk_bits(bits, chunk_size):
    """Break bits into chunks for encoding."""
    for chunk in chunks(bits, chunk_size):
        if len(chunk) < chunk_size:
            chunk += (0,) * (chunk_size - len(chunk))
            message = (f'word count not divisible by {chunk_size}; trailing '
                       f'zero(s) added')
            warnings.warn(message, RuntimeWarning)
        yield chunk


def deshebang(s, stype=None):
    """Remove a leading shebang line."""
    if stype is None:
        stype, s = stypes.probe(s)
    else:
        s = iter(s)
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
    """Split a text string-like on whitespace."""
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


class Peekable:
    """Iterator that supports far look-ahead."""

    def __init__(self, iterable):
        self._iterator = iter(iterable)
        self._queue = deque()
        self._peeker_ids = set()

    def __iter__(self):
        return self

    def __next__(self):
        self._peeker_ids.clear()
        if self._queue:
            return self._queue.popleft()
        return next(self._iterator)

    def _peeker(self, peeker_id):

        def check_advanced():
            if peeker_id not in self._peeker_ids:
                raise RuntimeError('peeker called after peekable advanced')

        check_advanced()
        for e in self._queue:
            yield e
            check_advanced()
        for e in self._iterator:
            self._queue.append(e)
            yield e
            check_advanced()

    def advance(self, stop):
        """Discard at most `stop` elements."""
        for _ in itertools.islice(self, stop):
            pass

    def peek(self, stop):
        """Peek ahead at the next `stop` elements (at most)."""
        if stop <= len(self._queue):
            return tuple(itertools.islice(self._queue, stop))
        self._queue.extend(itertools.islice(self._iterator,
                                            stop - len(self._queue)))
        return tuple(self._queue)

    def peek1(self):
        """Peek ahead 1 element, or raise `StopIteration`."""
        if self._queue:
            return self._queue[0]
        e = next(self._iterator)
        self._queue.append(e)
        return e

    def peeker(self):
        """Get a peeking iterator, subordinate to self.

        The iterator will break when self advances.
        """
        peeker_id = object()
        self._peeker_ids.add(peeker_id)
        return self._peeker(peeker_id)
