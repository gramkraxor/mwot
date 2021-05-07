import sys


def main(args=None, prefix_args=()):
    if args is None:
        args = sys.argv[1:]
    args = [*args, *prefix_args]
    print('Coming soon!', file=sys.stderr)
    sys.exit(1)


def mwot_i_bf(args=None):
    """Shebang helper to run brainfuck MWOT."""
    main(args, prefix_args=['-ib'])


def mwot_x_bf(args=None):
    """Shebang helper to run brainfuck."""
    main(args, prefix_args=['-xb'])
