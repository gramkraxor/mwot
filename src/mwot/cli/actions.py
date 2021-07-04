"""CLI actions: compile, decompile, interpret, execute."""

import sys
from pathlib import PurePath
import re

from ..compiler import bits_from_mwot
from .. import decompilers
from ..util import deshebang
from .exceptions import OutfileFormatError
from .parsing import unspecified
from .sources import get_sources

x_bf_shebang = '#!/usr/bin/env mwot-i-bf\n'
i_bf_shebang = b'#!/usr/bin/env mwot-x-bf\n'

re_double_braces = re.compile(r'\{\{|\}\}')
re_complex_specifier = re.compile(r'\{\w*[^\w{}]+\w*\}')


def buffer(textio, strtype):
    if strtype is bytes:
        return textio.buffer
    return textio


def format_outfile(pattern, pathstr):
    """Evaluate the -o pattern for a source file path."""
    # Reject format specifiers more complex than '{xyz}', such as
    # '{xyz + abc}' or '{xyz!r}'.
    cleaned = re_double_braces.sub('', pattern)
    if re_complex_specifier.search(cleaned):
        raise OutfileFormatError(f'bad outfile pattern: {pattern!r}')

    path = PurePath(pathstr)
    try:
        return pattern.format(
            name=path.name,
            file=path.name,
            stem=path.stem,
            root=path.stem,
            suffix=path.suffix,
            ext=path.suffix,
            path=path,
            parent=path.parent,
        )
    except (IndexError, KeyError, ValueError) as err:
        raise OutfileFormatError(f'bad outfile pattern: {pattern!r}') from err


def open_mode(str_mode, strtype):
    if strtype is bytes:
        return f'{str_mode}b'
    return f'{str_mode}t'


def specced(parsed, keywords):
    """Get a dictionary of non-`unspecified` attributes from `parsed`."""
    d = {}
    for k in keywords:
        v = getattr(parsed, k)
        if v is not unspecified:
            d[k] = v
    return d


class Action:
    """Base action."""

    keywords = ()

    def __init__(self, parsed, format_module):
        self.args = parsed
        self.format = format_module
        self.kwargs = specced(parsed, self.keywords)
        self.run()


class TranspilerAction(Action):

    def run(self):
        for source in get_sources(self.args, self.strtype_in):
            output = self.transpile(source.read())
            if self.args.outfile == '-':
                with buffer(sys.stdout, self.strtype_out) as f:
                    self.write(f, output)
            else:
                outfile_path = format_outfile(self.args.outfile,
                                              source.pathstr)
                mode = open_mode('w', self.strtype_out)
                with open(outfile_path, mode) as f:
                    self.write(f, output)

    def write(self, f, output):
        if self.args.shebang_out and self.args.format == 'brainfuck':
            f.write(self.bf_shebang)
        f.write(output)


class Compile(TranspilerAction):

    strtype_in = str
    strtype_out = bytes
    bf_shebang = b'#!/usr/bin/env mwot-x-bf\n'

    def transpile(self, source_code):
        return self.format.from_bits(bits_from_mwot(source_code)).join()

    def write(self, f, output):
        super().write(f, output)
        if self.args.format == 'brainfuck':
            f.write(b'\n')


class Decompile(TranspilerAction):

    strtype_in = bytes
    strtype_out = str
    bf_shebang = '#!/usr/bin/env mwot-i-bf\n'
    keywords = ('width', 'dummies', 'cols')

    def transpile(self, source_code):
        decomp = getattr(decompilers, self.args.decompiler).decomp
        if self.args.shebang_in:
            source_code = deshebang(source_code, bytes)
        return decomp(self.format.to_bits(source_code), **self.kwargs)


class InterpreterAction(Action):

    def run(self):
        source = get_sources(self.args, self.strtype_in)[0]
        self.execute(source.read())


class Interpret(InterpreterAction):

    strtype_in = str
    keywords = ('cellsize', 'eof', 'totalcells', 'wrapover')

    def execute(self, source_code):
        self.format.interpreter.run_mwot(source_code, **self.kwargs)


class Execute(InterpreterAction):

    strtype_in = bytes
    keywords = ('shebang_in', 'cellsize', 'eof', 'totalcells', 'wrapover')

    def execute(self, source_code):
        self.format.interpreter.run(source_code, **self.kwargs)
