"""Shared decompiling stuff."""

import textwrap

default_width = 72
default_dummies = ('zz', 'x')


def wrap_source(text, width=default_width):
    """Wrapping algorithm suitable for MWOT source."""
    if not width:
        return text
    lines = textwrap.wrap(text, width=width, break_long_words=False,
                          break_on_hyphens=False)
    return '\n'.join((*lines, ''))
