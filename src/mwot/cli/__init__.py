"""MWOT's CLI."""

import argparse
import sys
from .. import binary
from .. import brainfuck
from .actions import Compile, Decompile, Interpret, Execute
from .parsing import parse


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
    action_map = {
        'compile': Compile,
        'decompile': Decompile,
        'interpret': Interpret,
        'execute': Execute,
    }
    action = action_map[parsed.action]

    action(parsed, format_module)
    sys.exit(0)


def mwot_i_bf(args=None):
    """Shebang helper to run brainfuck MWOT."""
    main(args, prefix_args=['-ib'])


def mwot_x_bf(args=None):
    """Shebang helper to run brainfuck."""
    main(args, prefix_args=['-xb'])
