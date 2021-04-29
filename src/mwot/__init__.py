"""MWOT: an esolang."""

__all__ = [
    'CompilerError',
    'InterpreterError',
    'MWOTError',
    'bf_from_bits',
    'bf_from_mwot',
    'binary',
    'binary_from_mwot',
    'bits_from_bf',
    'bits_from_binary',
    'bits_from_mwot',
    'brainfuck',
    'cli',
    'run_bf',
    'run_mwot_bf',
]
__version__ = '0.0.0.dev0'

from . import binary
from . import brainfuck
from . import cli
from .compiler import bits_from_mwot
from .exceptions import CompilerError, InterpreterError, MWOTError
from .util import collectable

bf_from_bits = brainfuck.from_bits
bits_from_bf = brainfuck.to_bits
binary_from_bits = binary.from_bits
bits_from_binary = binary.to_bits

run_bf = brainfuck.interpreter.run
run_mwot_bf = brainfuck.interpreter.run_mwot


@collectable(bytes)
def bf_from_mwot(mwot):
    """Convert MWOT source to brainfuck."""
    return bf_from_bits(bits_from_mwot(mwot))


@collectable(bytes)
def binary_from_mwot(mwot):
    """Convert MWOT source to binary."""
    return binary_from_bits(bits_from_mwot(mwot))
