"""Run brainfuck."""

from collections import defaultdict
import sys

from ..compiler import bits_from_mwot
from .. import stypes
from ..util import deshebang
from . import cmds, from_bits as bf_from_bits


def get_jumps(instructions):
    """Match brackets and map their positions to each other."""
    stack = []
    jumps = {}
    for pc, cmd in enumerate(instructions):
        if cmd == '[':
            stack.append(pc)
        elif cmd == ']':
            try:
                target = stack.pop()
            except IndexError:
                raise ValueError("unmatched ']'") from None
            jumps[pc], jumps[target] = target, pc
    if stack:
        raise ValueError("unmatched '['")
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

    stype, brainfuck = stypes.probe(brainfuck, default=stypes.BYTES)
    if stype is not stypes.BYTES:
        raise TypeError('brainfuck must be bytes')
    if shebang_in:
        brainfuck = deshebang(brainfuck, stype)
    instructions = tuple(chr(c) for c in brainfuck if c in cmds)
    jumps = get_jumps(instructions)

    def shift(by):
        nonlocal pointer
        pointer += by
        if wraparound:
            if totalcells:
                pointer %= totalcells
        elif pointer < 0 or (totalcells and totalcells <= pointer):
            raise RuntimeError(f'pointer out of range: {pointer}')

    def increment(by):
        memory[pointer] += by
        if cellsize:
            cell_capacity = 1 << cellsize
            memory[pointer] %= cell_capacity

    def write():
        byte = memory[pointer] % 256
        bytestr = bytes((byte,))
        outfile.write(bytestr)
        outfile.flush()

    def read():
        char = infile.read(1)
        if char:
            (memory[pointer],) = char
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

    while pc < len(instructions):
        instruction_map[instructions[pc]]()
        pc += 1


def run_mwot(mwot, **options):
    """Compile MWOT to brainfuck and execute it."""
    run(bf_from_bits(bits_from_mwot(mwot)), shebang_in=False, **options)
