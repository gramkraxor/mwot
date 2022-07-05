"""CLI actions: compile, decompile, interpret, execute."""

import os
import stat
import sys

from ..compiler import bits_from_mwot
from .. import decompilers
from .. import stypes
from ..util import chunks, deshebang
from .parsing import Unspecified
from .sources import Source, StringSource


def chmod_x(f):
    """Set an open file as executable, if possible."""
    if not hasattr(os, 'fchmod'):
        return
    fd = f.fileno()
    st_mode = os.stat(fd).st_mode
    if stat.S_ISREG(st_mode):  # Only change regular files.
        mask = os.umask(0o077)
        os.umask(mask)
        mode = stat.S_IMODE(st_mode | (0o111 & ~mask))
        os.fchmod(fd, mode)


def specced(namespace, keywords):
    """Get a dictionary of non-`Unspecified` attributes."""
    specified = {}
    for keyword in keywords:
        value = getattr(namespace, keyword)
        if value is not Unspecified:
            specified[keyword] = value
    return specified


class Action:
    """Base action."""

    keywords = ()

    def __init__(self, parsed, format_module):
        self.args = parsed
        self.format = format_module
        self.kwargs = specced(parsed, self.keywords)
        self.run()

    def get_source(self):
        """Retrieve the correct code source."""
        if self.args.source is not None:
            string = self.stype_in.convert(self.args.source)
            return StringSource(string)
        return Source(self.args.srcfile, self.stype_in)

    def open_outfile(self):
        """Open the correct output file."""
        if self.args.outfile == '-':
            return self.stype_out.buffer(sys.stdout)
        mode = self.stype_out.iomode('w')
        return open(self.args.outfile, mode)


class TranspilerAction(Action):

    def run(self):
        source = self.get_source()
        output = self.transpile(source.read())
        with self.open_outfile() as f:
            self.write(f, output)

    def write(self, f, output):
        if self.args.shebang_out and self.args.format == 'brainfuck':
            f.write(self.bf_shebang)
        if self.stype_out is stypes.Bytes:
            for chunk in chunks(output, 80):
                f.write(bytes(chunk))
        else:
            for i in output:
                f.write(i)


class Compile(TranspilerAction):

    stype_in = stypes.Str
    stype_out = stypes.Bytes
    bf_shebang = b'#!/usr/bin/env -S mwot -xb\n'

    def transpile(self, source_code):
        return self.format.from_bits(bits_from_mwot(source_code))

    def write(self, f, output):
        if self.args.executable_out:
            chmod_x(f)
        super().write(f, output)
        if self.args.format == 'brainfuck':
            f.write(b'\n')


class Decompile(TranspilerAction):

    stype_in = stypes.Bytes
    stype_out = stypes.Str
    bf_shebang = '#!/usr/bin/env -S mwot -ib\n'
    keywords = ('width', 'vocab', 'cols')

    def transpile(self, source_code):
        decomp = getattr(decompilers, self.args.decompiler).decomp
        if self.args.shebang_in and self.args.format == 'brainfuck':
            source_code = deshebang(source_code, self.stype_in)
        return decomp(self.format.to_bits(source_code), **self.kwargs)

    def write(self, f, output):
        if self.args.executable_out and self.args.format == 'brainfuck':
            chmod_x(f)
        super().write(f, output)


class InterpreterAction(Action):

    stype_out = stypes.Bytes

    def get_input(self):
        """Retrieve the correct interpreter input source."""
        if self.args.input is not None:
            return StringSource(self.args.input.encode())
        if self.args.infile != '-':
            return Source(self.args.infile, stypes.Bytes)
        if self.args.source is None and self.args.srcfile == '-':
            return StringSource(b'')
        return Source('-', stypes.Bytes)

    def run(self):
        source_code = self.get_source().read()
        with self.get_input().open() as infile, self.open_outfile() as outfile:
            self.kwargs['infile'] = infile
            self.kwargs['outfile'] = outfile
            self.execute(source_code)


class Interpret(InterpreterAction):

    stype_in = stypes.Str
    keywords = ('cellsize', 'eof', 'totalcells', 'wraparound')

    def execute(self, source_code):
        self.format.interpreter.run_mwot(source_code, **self.kwargs)


class Execute(InterpreterAction):

    stype_in = stypes.Bytes
    keywords = ('shebang_in', 'cellsize', 'eof', 'totalcells', 'wraparound')

    def execute(self, source_code):
        self.format.interpreter.run(source_code, **self.kwargs)
