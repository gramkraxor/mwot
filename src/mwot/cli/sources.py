"""Different ways to feed source code to the CLI."""

import io
import sys


class Source:
    """Source file/string type."""

    def __init__(self, pathstr, stype):
        self.pathstr = pathstr
        self.stype = stype

    def open(self):
        if self.pathstr == '-':
            if self.stype is bytes:
                return sys.stdin.buffer
            return sys.stdin
        mode = 'rb' if self.stype is bytes else 'r'
        return open(self.pathstr, mode)

    def read(self):
        with self.open() as f:
            return f.read()


class StringSource(Source):
    """Source string type."""

    def __init__(self, string):
        stype = bytes if isinstance(string, bytes) else str
        super().__init__('-', stype)
        self.string = string

    def open(self):
        if self.stype is bytes:
            return io.BytesIO(self.string)
        return io.StringIO(self.string)

    def read(self):
        return self.string


def get_sources(parsed, stype):
    """Retrieve the correct source(s) from `parsed`."""
    if parsed.source is not None:
        string = parsed.source.encode() if stype is bytes else parsed.source
        return [StringSource(string)]
    if parsed.srcfiles:
        return [Source(i, stype) for i in parsed.srcfiles]
    return [Source('-', stype)]
