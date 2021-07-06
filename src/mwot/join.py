"""The Joinable interface for collecting iterators."""

from functools import wraps


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
