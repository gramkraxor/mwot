"""Run brainfuck."""

from collections import defaultdict
import sys

from ..compiler import bits_from_mwot
from .. import stypes
from ..util import Peekable, deshebang
from . import cmds, from_bits as bf_from_bits

_OP_SHIFT = object()
_OP_INC = object()
_OP_OUT = object()
_OP_IN = object()
_OP_OPEN = object()
_OP_CLOSE = object()
_OP_SET = object()
_OP_SCAN = object()
_OP_MUL = object()


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
    cell_mask = ~(~0 << cellsize) if cellsize else ~0
    memory = [0] * totalcells if totalcells else defaultdict(int)
    stype, brainfuck = stypes.probe(brainfuck, default=stypes.BYTES)
    if stype is not stypes.BYTES:
        raise TypeError('brainfuck must be bytes')
    if shebang_in:
        brainfuck = deshebang(brainfuck, stype)
    ops = _make_program(chr(c) for c in brainfuck if c in cmds)
    ops = _opt_set(ops)
    ops = _opt_scan(ops)
    ops = _opt_mul(ops)
    program = tuple(ops)
    jumps = _get_jumps(program)
    pc = 0
    pointer = 0

    def pointer_too_low():
        raise RuntimeError('pointer out of range (< 0)')

    def pointer_too_high():
        raise RuntimeError(f'pointer out of range (> {len(memory) - 1})')

    while pc < len(program):
        opcode, op_arg = program[pc]
        if opcode is _OP_SHIFT:
            pointer += op_arg
            if wraparound:
                if totalcells:
                    pointer %= totalcells
            elif pointer < 0:
                pointer_too_low()
            elif totalcells and pointer >= totalcells:
                pointer_too_high()
        elif opcode is _OP_INC:
            memory[pointer] = (memory[pointer] + op_arg) & cell_mask
        elif opcode is _OP_OPEN:
            if not memory[pointer]:
                pc = jumps[pc]
        elif opcode is _OP_CLOSE:
            if memory[pointer]:
                pc = jumps[pc]
        elif opcode is _OP_SET:
            memory[pointer] = op_arg & cell_mask
        elif opcode is _OP_MUL:
            cell_value = memory[pointer]
            if cell_value:
                negative, muls = op_arg
                if negative:
                    cell_value = -cell_value
                for offset, scalar in muls:
                    mul_pointer = pointer + offset
                    if wraparound:
                        if totalcells:
                            mul_pointer %= totalcells
                    elif mul_pointer < 0:
                        pointer_too_low()
                    elif totalcells and mul_pointer >= totalcells:
                        pointer_too_high()
                    memory[mul_pointer] = (
                        memory[mul_pointer] + cell_value * scalar) & cell_mask
                memory[pointer] = 0
        elif opcode is _OP_SCAN:
            while memory[pointer]:
                pointer += op_arg
                if wraparound:
                    if totalcells:
                        pointer %= totalcells
                elif pointer < 0:
                    pointer_too_low()
                elif totalcells and pointer >= totalcells:
                    pointer_too_high()
        elif opcode is _OP_OUT:
            byte = memory[pointer] & 0xff
            outfile.write(bytes((byte,)))
            outfile.flush()
        elif opcode is _OP_IN:
            char = infile.read(1)
            if char:
                (memory[pointer],) = char
            elif eof is not None:
                memory[pointer] = eof
        else:
            raise ValueError(f'unknown opcode: {opcode!r}')
        pc += 1


def run_mwot(mwot, **options):
    """Compile MWOT to brainfuck and execute it."""
    run(bf_from_bits(bits_from_mwot(mwot)), shebang_in=False, **options)


def _make_program(instructions):
    """Convert brainfuck instructions to opcodes (and their arguments)."""
    instructions = Peekable(instructions)
    for instr in instructions:
        if instr == '>':
            n = 0
            for n, instr_1 in enumerate(instructions.peeker(), 1):
                if instr_1 != '>':
                    n -= 1
                    break
            instructions.advance(n)
            yield (_OP_SHIFT, n + 1)
        elif instr == '<':
            # To enforce pointer bounds, don't combine left and right shifts.
            n = 0
            for n, instr_1 in enumerate(instructions.peeker(), 1):
                if instr_1 != '<':
                    n -= 1
                    break
            instructions.advance(n)
            yield (_OP_SHIFT, -(n + 1))
        elif (pos := instr == '+') or instr == '-':
            inc = 1 if pos else -1
            n = 0
            for n, instr_1 in enumerate(instructions.peeker(), 1):
                if instr_1 == '+':
                    inc += 1
                elif instr_1 == '-':
                    inc -= 1
                else:
                    n -= 1
                    break
            instructions.advance(n)
            if inc:
                yield (_OP_INC, inc)
        elif instr == '.':
            yield (_OP_OUT, None)
        elif instr == ',':
            yield (_OP_IN, None)
        elif instr == '[':
            yield (_OP_OPEN, None)
        elif instr == ']':
            yield (_OP_CLOSE, None)
        else:
            raise ValueError(f'unknown instruction: {instr!r}')


def _opt_set(ops):
    """Optimize constant value assignments (like `[-]` or `[+]++`)."""
    ops = Peekable(ops)
    for opcode, op_arg in ops:
        if opcode is _OP_OPEN:
            peeker = ops.peeker()
            opcode_1, op_arg_1 = next(peeker, (None, None))
            if opcode_1 is not _OP_INC or not op_arg_1 % 2:
                yield (opcode, op_arg)
                continue
            opcode_2, _ = next(peeker, (None, None))
            if opcode_2 is not _OP_CLOSE:
                yield (opcode, op_arg)
                continue
            opcode_3, op_arg_3 = next(peeker, (None, None))
            if opcode_3 is _OP_INC:
                yield (_OP_SET, op_arg_3)
                ops.advance(3)
            else:
                yield (_OP_SET, 0)
                ops.advance(2)
        else:
            yield (opcode, op_arg)


def _opt_scan(ops):
    """Optimize shift-until-zero operations (like `[<<]`)."""
    ops = Peekable(ops)
    for opcode, op_arg in ops:
        if opcode is _OP_OPEN:
            peeker = ops.peeker()
            opcode_1, op_arg_1 = next(peeker, (None, None))
            if opcode_1 is not _OP_SHIFT:
                yield (opcode, op_arg)
                continue
            opcode_2, _ = next(peeker, (None, None))
            if opcode_2 is not _OP_CLOSE:
                yield (opcode, op_arg)
                continue
            yield (_OP_SCAN, op_arg_1)
            ops.advance(2)
        else:
            yield (opcode, op_arg)


def _opt_mul(ops):
    """Optimize move/multiply operations (like `[->>+<<]` or `[->++<]`).

    Multiple increments are supported, including `[>+>++<<-]` and
    `[+>+>+<+<]`. The starting cell must be incremented by exactly 1 or
    -1 by the end of the loop body.
    """
    ops = Peekable(ops)
    for opcode, op_arg in ops:
        if opcode is _OP_OPEN:
            peeker = ops.peeker()
            offset = 0
            muls_map = {0: 0}
            n = None
            opcode_1 = None
            for n, (opcode_1, op_arg_1) in enumerate(peeker, 1):
                if opcode_1 is _OP_SHIFT:
                    offset += op_arg_1
                    muls_map.setdefault(offset, 0)
                elif opcode_1 is _OP_INC:
                    muls_map[offset] += op_arg_1
                else:
                    break
            if (opcode_1 is not _OP_CLOSE or offset != 0
                    or abs(muls_map[0]) != 1):
                yield (opcode, op_arg)
                continue
            ops.advance(n)
            # Include max and min offsets, even if they weren't
            # incremented, to enforce pointer bounds.
            offset_extrema = (min(muls_map), max(muls_map))
            muls = tuple((o, s) for o, s in muls_map.items()
                         if o and (s or o in offset_extrema))
            yield (_OP_MUL, (muls_map[0] == 1, muls))
        else:
            yield (opcode, op_arg)


def _get_jumps(program):
    """Match brackets and map their positions to each other."""
    stack = []
    jumps = {}
    for pc, (opcode, _) in enumerate(program):
        if opcode is _OP_OPEN:
            stack.append(pc)
        elif opcode is _OP_CLOSE:
            try:
                target = stack.pop()
            except IndexError:
                raise ValueError("unmatched ']'") from None
            jumps[pc], jumps[target] = target, pc
    if stack:
        raise ValueError("unmatched '['")
    return jumps
