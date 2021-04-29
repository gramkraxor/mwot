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
]
__version__ = '0.0.0.dev0'

from . import binary
from . import brainfuck
from . import cli
from .compiler import bits_from_mwot
from .exceptions import CompilerError, InterpreterError, MWOTError

bf_from_bits = brainfuck.from_bits
bits_from_bf = brainfuck.to_bits
binary_from_bits = binary.from_bits
bits_from_binary = binary.to_bits


def bf_from_mwot(mwot):
    """Convert MWOT source to brainfuck."""
    return brainfuck.from_bits(bits_from_mwot(mwot))


def binary_from_mwot(mwot):
    """Convert MWOT source to binary."""
    return bytes.from_bits(bits_from_mwot(mwot))
