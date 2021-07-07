"""Different ways to feed source code to the CLI."""

import sys

from .. import stypes


class Source:
    """Source file/string type."""

    def __init__(self, pathstr, stype):
        self.pathstr = pathstr
        self.stype = stype

    def open(self):
        if self.pathstr == '-':
            return self.stype.buffer(sys.stdin)
        mode = self.stype.iomode('r')
        return open(self.pathstr, mode)

    def read(self):
        with self.open() as f:
            return f.read()


class StringSource(Source):
    """Source string type."""

    def __init__(self, string):
        stype = stypes.ask(string)
        super().__init__('-', stype)
        self.string = string

    def open(self):
        return stypes.StringIO(self.string)

    def read(self):
        return self.string
