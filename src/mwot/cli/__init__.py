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

    try:
        action(parsed, format_module)
    except (KeyboardInterrupt, BrokenPipeError):
        pass
    sys.exit(0)
