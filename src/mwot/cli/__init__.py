"""MWOT's CLI."""

import argparse
import sys
from .. import binary
from .. import brainfuck
from ..compiler import bits_from_mwot
from .. import decompilers
from ..util import deshebang
from .parsing import parse, unspecified

i_bf_shebang = '#!/usr/bin/env mwot-i-bf\n'
x_bf_shebang = b'#!/usr/bin/env mwot-x-bf\n'


def specced(parsed, keywords):
    """Get a dictionary of non-`unspecified` attributes from `parsed`."""
    d = {}
    for k in keywords:
        v = getattr(parsed, k)
        if v is not unspecified:
            d[k] = v
    return d


def compile_action(parsed, format_module):
    mwot = sys.stdin.read()
    if parsed.shebang_out and parsed.format == 'brainfuck':
        sys.stdout.buffer.write(x_bf_shebang)
    output = format_module.from_bits(bits_from_mwot(mwot)).join()
    sys.stdout.buffer.write(output)
    if parsed.format == 'brainfuck':
        sys.stdout.buffer.write(b'\n')


def decompile_action(parsed, format_module):
    decompiler = getattr(decompilers, parsed.decompiler).decomp
    kwargs = specced(parsed, ('width', 'dummies', 'cols'))
    source = sys.stdin.buffer.read()
    if parsed.shebang_in:
        source = deshebang(source, bytes)
    mwot = decompiler.decomp(format_module.to_bits(source), **kwargs)
    if parsed.shebang_out and parsed.format == 'brainfuck':
        sys.stdout.write(i_bf_shebang)
    sys.stdout.write(mwot)


def interpret_action(parsed, format_module):
    keywords = ('cellsize', 'eof', 'totalcells', 'wrapover')
    kwargs = specced(parsed, keywords)
    format_module.interpreter.run_mwot(sys.stdin.read(), **kwargs)


def execute_action(parsed, format_module):
    keywords = ('shebang_in', 'cellsize', 'eof', 'totalcells', 'wrapover')
    kwargs = specced(parsed, keywords)
    format_module.interpreter.run(sys.stdin.buffer.read(), **kwargs)


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
