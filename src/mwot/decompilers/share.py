"""Shared decompiling stuff."""

from ..join import joinable

default_width = 72
default_dummies = ('zz', 'x')


@joinable(str)
def wrap_words(words, width=default_width):
    """Wrap the words at a given length.

    Takes an iterable of word strings and returns joinable line strings.
    """
    if not width:
        joined = ' '.join(words)
        yield f'{joined}\n'
        return
    line_words = []
    line_width = -1
    for word in words:
        if line_words and line_width + 1 + len(word) > width:
            joined = ' '.join(line_words)
            yield f'{joined}\n'
            line_words.clear()
            line_width = -1
        line_words.append(word)
        line_width += 1 + len(word)
    if line_words:
        joined = ' '.join(line_words)
        yield f'{joined}\n'
