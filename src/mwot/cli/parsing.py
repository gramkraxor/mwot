"""The `argparse`-based portion of the CLI."""

import argparse

from .. import __version__
from ..decompilers.common import default_dummies, default_width
from .argtypes import (ArgUnion, BooleanArg, DecompilerArg, IntArg, NoneArg,
                       NonnegIntArg, PosIntArg, VocabArg)

description = """

Usage:
  mwot -(c|d)(b|B) [SRCFILE...]
  mwot -(i|x)b [SRCFILE]

MWOT: an esoteric... language? Encoding?

"""

epilog = """

More help coming soon!

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
        '-b', '--brainfuck', '--bf',
        dest='format',
        action='store_const',
        const='brainfuck',
        help='use brainfuck format',
    )
    format_mx_opts.add_argument(
        '-B', '--bytes', '--binary',
        dest='format',
        action='store_const',
        const='binary',
        help='use bytes format',
    )
    srcfiles_opt = main_opts.add_argument(
        'srcfiles',
        metavar='SRCFILE',
        nargs='*',
        help="source file(s) (absent or '-' for stdin)",
    )
    source_opt = main_opts.add_argument(
        '--source',
        dest='source',
        metavar='SOURCE',
        help="take source code as an argument; don't accept SRCFILE",
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
        '-o', '--output-file',
        dest='outfile',
        metavar='OUTFILE',
        default='-',
        help="output file pattern (absent or '-' for stdout)",
    )
    trans_opts.add_argument(
        '-S', '--shebang-out',
        action='store_true',
        help='(with -b) include a shebang in output',
    )
    trans_opts.add_argument(
        '-X', '--executable-out',
        action='store_true',
        help='(with -b or -cB) make output files executable',
    )

    decomp_opts.add_argument(
        '-D', '--decompiler',
        metavar='DECOMPILER',
        type=DecompilerArg,
        default='rand',
        help='decompiler to use (default: rand)',
    )
    default_vocab_str = repr(' '.join(default_dummies))
    decomp_opts.add_argument(
        '--vocab',
        dest='dummies',
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
        help=f"(basic, rand) wrap width (default: {default_width})",
    )
    decomp_opts.add_argument(
        '--cols',
        metavar='COLS',
        type=PosIntArg,
        default=Unspecified,
        help="(guide) bits per row (default: 8)",
    )

    bf_src_opts.add_argument(
        '--shebang-in',
        action='store_true',
        help='skip over any shebang in source (default)',
    )
    bf_src_opts.add_argument(
        '--no-shebang-in',
        dest='shebang_in',
        action='store_false',
        help='treat any shebang in source as literal brainfuck',
    )
    parser.set_defaults(shebang_in=True)

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
        help=('int to read in after EOF, or \'none\' for "no change" behavior '
              '(default: none)'),
    )
    i_bf_opts.add_argument(
        '--totalcells',
        metavar='CELLS',
        type=NonnegIntArg,
        default=Unspecified,
        help='total cells (0 for dynamic allocation) (default: 30_000)',
    )
    i_bf_opts.add_argument(
        '--wrapover',
        metavar='BOOL',
        type=BooleanArg,
        default=Unspecified,
        help=('whether the cell pointer wraps around / whether "dynamic '
              'allocation" includes negative indices (default: true)'),
    )

    parsed = parser.parse_args(args)

    # Manually add some restrictions and adjustments.
    if parsed.source is not None and parsed.srcfiles:
        srcfile = srcfiles_opt.metavar
        source = '/'.join(source_opt.option_strings)
        parser.error(f'argument {source}: not allowed with argument {srcfile}')
    if not parsed.srcfiles:
        parsed.srcfiles = ['-']
    if parsed.action in ('interpret', 'execute'):
        if parsed.format != 'brainfuck':
            parser.error(f'cannot execute {parsed.format}')
        if len(parsed.srcfiles) > 1:
            parser.error('cannot execute multiple source files')
    else:
        if parsed.outfile == '-' and len(parsed.srcfiles) > 1:
            parser.error('cannot transpile multiple source files to stdout')
    if parsed.srcfiles.count('-') > 1:
        parser.error('cannot open stdin multiple times')

    return parser, parsed
