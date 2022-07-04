"""The `argparse`-based portion of the CLI."""

import argparse
import sys

from .. import __version__
from ..decompilers.common import default_vocab, default_width
from .argtypes import (ArgUnion, BooleanArg, DecompilerArg, IntArg, NoneArg,
                       PosIntArg, VocabArg)

description = """

Usage:
  mwot -(c|d)(b|y) [SRCFILE]
  mwot -(i|x)b [SRCFILE]

Transpile MWOT or execute brainfuck.

"""

epilog = """

Available decompilers (-D):
  basic      one word for 0, one word for 1
  guide      guide to help you write MWOT
  rand       random letters

"""

Unspecified = object()  # Indicates that kwargs should not be passed


def parse(args):
    parser = argparse.ArgumentParser(
        prog='mwot',
        usage=argparse.SUPPRESS,
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )

    main_opts = parser.add_argument_group(
        'Main options')
    trans_opts = parser.add_argument_group(
        'Transpilation (-[cd]) options')
    decomp_opts = parser.add_argument_group(
        'Decompilation (-d) options')
    bf_src_opts = parser.add_argument_group(
        'Brainfuck source (-[dx]b) options')
    i_bf_opts = parser.add_argument_group(
        'Brainfuck interpreter (-[ix]b) options')

    action_mx_opts = main_opts.add_mutually_exclusive_group(required=True)
    format_mx_opts = main_opts.add_mutually_exclusive_group(required=True)
    src_mx_opts = main_opts.add_mutually_exclusive_group(required=False)
    action_mx_opts.add_argument(
        '-c', '--compile',
        dest='action',
        action='store_const',
        const='compile',
        help='compile MWOT',
    )
    action_mx_opts.add_argument(
        '-d', '--decompile',
        dest='action',
        action='store_const',
        const='decompile',
        help='decompile to MWOT',
    )
    action_mx_opts.add_argument(
        '-i', '--interpret',
        dest='action',
        action='store_const',
        const='interpret',
        help='(with -b) execute MWOT as brainfuck',
    )
    action_mx_opts.add_argument(
        '-x', '--execute',
        dest='action',
        action='store_const',
        const='execute',
        help='(with -b) execute brainfuck',
    )
    format_mx_opts.add_argument(
        '-b', '--brainfuck',
        dest='format',
        action='store_const',
        const='brainfuck',
        help='use brainfuck format',
    )
    format_mx_opts.add_argument(
        '-y', '--binary',
        dest='format',
        action='store_const',
        const='binary',
        help='use binary (octets) format',
    )
    src_mx_opts.add_argument(
        'srcfile',
        metavar='SRCFILE',
        nargs='?',
        help="source file (absent or '-' for stdin)",
    )
    src_mx_opts.add_argument(
        '--source',
        dest='source',
        metavar='SOURCE',
        help="take source code as an argument; don't accept SRCFILE",
    )
    main_opts.add_argument(
        '-o', '--output-file',
        dest='outfile',
        metavar='OUTFILE',
        default='-',
        help="output file (absent or '-' for stdout)",
    )
    main_opts.add_argument(
        '--help',
        action='help',
        help='show this help and exit',
    )
    main_opts.add_argument(
        '--version',
        action='version',
        version=f'mwot {__version__}',
        help='show version info and exit',
    )

    trans_opts.add_argument(
        '-S', '--shebang-out',
        action='store_true',
        help='(with -b) include a shebang in output',
    )
    trans_opts.add_argument(
        '-X', '--executable-out',
        action='store_true',
        help='(with -b or -cy) make output files executable',
    )

    decomp_opts.add_argument(
        '-D', '--decompiler',
        metavar='DECOMPILER',
        type=DecompilerArg,
        default='rand',
        help='decompiler to use (default: rand)',
    )
    default_vocab_str = repr(' '.join(default_vocab))
    decomp_opts.add_argument(
        '--vocab',
        metavar='WORDS',
        type=VocabArg,
        default=Unspecified,
        help=(f'(basic, guide) words for zero and one (default: '
              f'{default_vocab_str})'),
    )
    decomp_opts.add_argument(
        '--width',
        metavar='WIDTH',
        type=ArgUnion(PosIntArg, NoneArg),
        default=Unspecified,
        help=(f"(basic, rand) wrap width ('none' for no wrapping) (default: "
              f"{default_width})"),
    )
    decomp_opts.add_argument(
        '--cols',
        metavar='COLS',
        type=PosIntArg,
        default=Unspecified,
        help="(guide) bits per row (default: 8)",
    )

    bf_src_opts.add_argument(
        '--no-shebang-in',
        dest='shebang_in',
        action='store_false',
        help='treat a shebang as literal brainfuck',
    )

    input_mx_opts = i_bf_opts.add_mutually_exclusive_group()
    input_mx_opts.add_argument(
        '--input-file',
        dest='infile',
        metavar='INFILE',
        default='-',
        help="read input from INFILE (absent or '-' for stdin if possible)",
    )
    input_mx_opts.add_argument(
        '--input',
        metavar='INPUT',
        help='take input as an argument',
    )
    i_bf_opts.add_argument(
        '--cellsize',
        metavar='BITS',
        type=ArgUnion(PosIntArg, NoneArg),
        default=Unspecified,
        help='bits per cell (default: 8)',
    )
    i_bf_opts.add_argument(
        '--eof',
        metavar='VAL',
        type=ArgUnion(IntArg, NoneArg),
        default=Unspecified,
        help=('int to read in after EOF (\'none\' for "no change" behavior) '
              '(default: none)'),
    )
    i_bf_opts.add_argument(
        '--totalcells',
        metavar='CELLS',
        type=ArgUnion(PosIntArg, NoneArg),
        default=Unspecified,
        help="total cells ('none' for dynamic size) (default: 30_000)",
    )
    i_bf_opts.add_argument(
        '--wraparound',
        metavar='BOOL',
        type=BooleanArg,
        default=Unspecified,
        help='whether the cell pointer can overflow (default: true)',
    )

    if not args:
        parser.print_help()
        sys.exit(1)

    parsed = parser.parse_args(args)

    # Manually add some restrictions and adjustments.
    if parsed.srcfile is None:
        parsed.srcfile = '-'
    if parsed.action in ('interpret', 'execute'):
        if parsed.format != 'brainfuck':
            parser.error(f'cannot execute {parsed.format}')

    return parser, parsed
