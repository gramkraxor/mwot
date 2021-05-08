"""The `argparse`-based portion of the CLI."""

import argparse
from .. import __version__

description = """

Usage: mwot OPTIONS [SRCFILE...]

MWOT: an esolang.

"""

epilog = """

Coming soon!

"""


def parse(args):
    parser = argparse.ArgumentParser(
        usage=argparse.SUPPRESS,
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )

    main_options = parser.add_argument_group('Main options')

    main_options.add_argument(
        '--help',
        action='help',
        help='show this help message and exit',
    )
    main_options.add_argument(
        '--version',
        action='version',
        version=f'mwot {__version__}',
        help='show version info and exit',
    )

    parsed = parser.parse_args(args)

    return parser, parsed
