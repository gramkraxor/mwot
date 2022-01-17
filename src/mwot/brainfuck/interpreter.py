"""Run brainfuck."""

from collections import defaultdict
import sys

from ..compiler import bits_from_mwot
from ..exceptions import InterpreterError
from ..join import joinable
from ..util import deshebang
from . import cmds, from_bits as bf_from_bits

# Map bytes and str cmds to str cmds
cmds_str = cmds.decode('ascii')
decoder = {k: v for i in (cmds, cmds_str) for k, v in zip(i, cmds_str)}


@joinable(str)
def clean_bf(s):
    """Remove non-brainfuck characters and convert to `str` string-like."""
    for char in s:
        cmd = decoder.get(char)
        if cmd is not None:
            yield cmd


def get_jumps(brainfuck):
    """Match brackets and map their positions to each other."""
    stack = []
    jumps = {}
    for pc, cmd in enumerate(brainfuck):
        if cmd == '[':
            stack.append(pc)
        elif cmd == ']':
            try:
                target = stack.pop()
            except IndexError:
                raise InterpreterError("unmatched ']'") from None
            jumps[pc], jumps[target] = target, pc
    if stack:
        raise InterpreterError("unmatched '['")
    return jumps


def run(brainfuck, infile=None, outfile=None, cellsize=8, eof=None,
        shebang_in=True, totalcells=30_000, wraparound=True):
    """Run brainfuck code.

    I/O is done in `bytes`, not `str`.

    Implementation options:
        cellsize: Size of each cell, in bits. Can be falsy for no limit.
        eof: What to do for input after EOF. Can be a fill value to read
            in or None for "no change".
        shebang_in: Whether a leading shebang will be recognized and
            ignored.
        totalcells: Number of cells. Can be falsy for dynamic size.
        wraparound: Whether to overflow instead of error when the
            pointer goes out of bounds. Also determines whether "dynamic
            size" includes negative indices.

    infile and outfile default to sys.stdin.buffer and
    sys.stdout.buffer, respectively.
    """
    if infile is None:
        infile = sys.stdin.buffer
    if outfile is None:
        outfile = sys.stdout.buffer
    if totalcells:
        memory = [0] * totalcells
    else:
        memory = defaultdict(lambda: 0)
    pc = 0
    pointer = 0

    if shebang_in:
        brainfuck = deshebang(brainfuck)
    brainfuck = clean_bf(brainfuck).join()
    jumps = get_jumps(brainfuck)

    def shift(by):
        nonlocal pointer
        pointer += by
        if wraparound:
            if totalcells:
                pointer %= totalcells
        elif pointer < 0 or (totalcells and totalcells <= pointer):
            raise InterpreterError(f'pointer out of range: {pointer}')

    def increment(by):
        memory[pointer] += by
        if cellsize:
            cell_capacity = 1 << cellsize
            memory[pointer] %= cell_capacity

    def write():
        byte = memory[pointer] % 256
        bytestr = bytes((byte,))
        outfile.write(bytestr)
        if outfile.isatty():
            outfile.flush()

    def read():
        char = infile.read(1)
        if char:
            memory[pointer] = char[0]
        elif eof is not None:
            memory[pointer] = eof

    def jump(truthiness):
        nonlocal pc
        if bool(memory[pointer]) == truthiness:
            pc = jumps[pc]

    instruction_map = {
        '>': lambda: shift(1),
        '<': lambda: shift(-1),
        '+': lambda: increment(1),
        '-': lambda: increment(-1),
        '.': write,
        ',': read,
        '[': lambda: jump(False),
        ']': lambda: jump(True),
    }

    while pc < len(brainfuck):
        instruction_map[brainfuck[pc]]()
        pc += 1


def run_mwot(mwot, **options):
    """Compile MWOT to brainfuck and execute it."""
    run(bf_from_bits(bits_from_mwot(mwot)), shebang_in=False, **options)
