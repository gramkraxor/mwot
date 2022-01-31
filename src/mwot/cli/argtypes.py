"""Fancy argparse type conversion."""

import re

from ..compiler import bits_from_mwot
from ..util import split

truthies = {'true', 't', 'yes', 'y', '1'}
falsies = {'false', 'f', 'no', 'n', '0'}
decomps = {'basic', 'guide', 'rand'}

re_double_braces = re.compile(r'\{\{|\}\}')
re_complex_specifier = re.compile(r'\{[^}]*[^\w}][^}]*\}')
outfile_sub_names = ('name', 'stem', 'suffix', 'path', 'dir')


class ArgType:
    """Argparse option type with a display name."""

    def __init__(self, name, function, casefold=True):
        self.name = name
        self.function = function
        self.casefold = casefold

    def __call__(self, val):
        """Convert a string to the correct type.

        Raises ValueError if that's not possible.
        """
        if self.casefold:
            val = val.casefold()
        return self.function(val)

    def __repr__(self):
        return self.name


def argtype(name, casefold=True):
    """Turn a function into an ArgType."""

    def decorator(fn):
        return ArgType(name, fn, casefold=casefold)

    return decorator


def ArgUnion(*argtypes):
    """Create a union of arg types."""
    name = ' or '.join(i.name for i in argtypes).replace(' ', '-')

    def function(val):
        for atype in argtypes:
            try:
                return atype(val)
            except ValueError:
                pass
        raise ValueError('unknown type')

    return ArgType(name, function)


@argtype('boolean')
def BooleanArg(val):
    if val in truthies:
        return True
    if val in falsies:
        return False
    raise ValueError('unknown boolean keyword')


@argtype('decompiler')
def DecompilerArg(val):
    if val in decomps:
        return val
    raise ValueError('unknown decompiler')


@argtype('integer')
def IntArg(val):
    return int(val)


@argtype('none')
def NoneArg(val):
    if val != 'none':
        raise ValueError('not none')
    return None


@argtype('outfile pattern', casefold=False)
def OutfileArg(val):
    # Reject format specifiers more complex than '{xyz}', such as
    # '{xyz:6}' or '{xyz!r}'.
    cleaned = re_double_braces.sub('', val)
    if re_complex_specifier.search(cleaned):
        raise ValueError('complex format specifier')

    # Test that formatting works.
    subs = {n: '' for n in outfile_sub_names}
    try:
        val.format(**subs)
    except (LookupError, ValueError) as err:
        raise ValueError('nonexistent substitution') from err

    return val


@argtype('positive integer')
def PosIntArg(val):
    num = int(val)
    if num <= 0:
        raise ValueError('nonpositive int')
    return num


@argtype('vocab', casefold=False)
def VocabArg(val):
    desired = (0, 1)
    words = tuple(split(val))
    if len(words) != len(desired):
        raise ValueError('wrong number of words')
    if tuple(bits_from_mwot(val)) != desired:
        raise ValueError(f'bits not {desired}')
    return words
