"""MWOT's CLI."""

import argparse
import io
from pathlib import Path, PurePath
import re
import sys
from .. import binary
from .. import brainfuck
from ..compiler import bits_from_mwot
from .. import decompilers
from ..util import deshebang
from .exceptions import OutfileFormatError
from .parsing import parse, unspecified

i_bf_shebang = '#!/usr/bin/env mwot-i-bf\n'
x_bf_shebang = b'#!/usr/bin/env mwot-x-bf\n'

re_double_braces = re.compile(r'\{\{|\}\}')
re_complex_specifier = re.compile(r'\{\w*[^\w{}]+\w*\}')


class Source:
    """Source file/string type."""

    def __init__(self, pathstr, strtype):
        self.pathstr = pathstr
        self.strtype = strtype

    def open(self):
        if self.pathstr == '-':
            if self.strtype is bytes:
                return sys.stdin.buffer
            return sys.stdin
        mode = 'rb' if self.strtype is bytes else 'r'
        return open(self.pathstr, mode)

    def read(self):
        with self.open() as f:
            return f.read()


class StringSource(Source):
    """Source string type."""

    def __init__(self, string):
        strtype = bytes if isinstance(string, bytes) else str
        super().__init__('-', strtype)
        self.string = string

    def open(self):
        if self.strtype is bytes:
            return io.BytesIO(self.string)
        return io.StringIO(self.string)

    def read(self):
        return self.string


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


def get_sources(parsed, strtype):
    """Retrieve the correct source(s) from `parsed`."""
    if parsed.source is not None:
        string = parsed.source.encode() if strtype is bytes else parsed.source
        return [StringSource(string)]
    if parsed.srcfiles:
        return [Source(i, strtype) for i in parsed.srcfiles]
    return [Source('-', strtype)]


def specced(parsed, keywords):
    """Get a dictionary of non-`unspecified` attributes from `parsed`."""
    d = {}
    for k in keywords:
        v = getattr(parsed, k)
        if v is not unspecified:
            d[k] = v
    return d


def compile_action(parsed, format_module):
    def write(f, output):
        if parsed.shebang_out and parsed.format == 'brainfuck':
            f.write(x_bf_shebang)
        f.write(output)
        if parsed.format == 'brainfuck':
            f.write(b'\n')

    for sourcefile in get_sources(parsed, str):
        source_code = sourcefile.read()
        output = format_module.from_bits(bits_from_mwot(source_code)).join()
        if parsed.outfile == '-':
            with sys.stdout.buffer as f:
                write(f, output)
        else:
            outfile_path = format_outfile(parsed.outfile, sourcefile.pathstr)
            with open(outfile_path, 'wb') as f:
                write(f, output)


def decompile_action(parsed, format_module):
    def write(f, output):
        if parsed.shebang_out and parsed.format == 'brainfuck':
            f.write(i_bf_shebang)
        f.write(output)

    decomp = getattr(decompilers, parsed.decompiler).decomp
    kwargs = specced(parsed, ('width', 'dummies', 'cols'))
    for sourcefile in get_sources(parsed, bytes):
        source_code = sourcefile.read()
        if parsed.shebang_in:
            source_code = deshebang(source_code, bytes)
        output = decomp(format_module.to_bits(source_code), **kwargs)
        if parsed.outfile == '-':
            with sys.stdout as f:
                write(f, output)
        else:
            outfile_path = format_outfile(parsed.outfile, sourcefile.pathstr)
            with open(outfile_path, 'w') as f:
                write(f, output)


def interpret_action(parsed, format_module):
    source = get_sources(parsed, str)[0]
    keywords = ('cellsize', 'eof', 'totalcells', 'wrapover')
    kwargs = specced(parsed, keywords)
    format_module.interpreter.run_mwot(source.read(), **kwargs)


def execute_action(parsed, format_module):
    source = get_sources(parsed, bytes)[0]
    keywords = ('shebang_in', 'cellsize', 'eof', 'totalcells', 'wrapover')
    kwargs = specced(parsed, keywords)
    format_module.interpreter.run(source.read(), **kwargs)


def main(args=None, prefix_args=()):
    if args is None:
        args = sys.argv[1:]
    args = [*prefix_args, *args]

    _, parsed = parse(args)

    format_modules = {
        'brainfuck': brainfuck,
        'binary': binary,
    }
    format_module = format_modules[parsed.format]
    actions = {
        'compile': compile_action,
        'decompile': decompile_action,
        'interpret': interpret_action,
        'execute': execute_action,
    }
    action = actions[parsed.action]

    action(parsed, format_module)
    sys.exit(0)


def mwot_i_bf(args=None):
    """Shebang helper to run brainfuck MWOT."""
    main(args, prefix_args=['-ib'])


def mwot_x_bf(args=None):
    """Shebang helper to run brainfuck."""
    main(args, prefix_args=['-xb'])
