__version__ = '0.0.0.dev0'

from . import binary
from . import brainfuck
from . import cli
from .compiler import mwot_to_bits
from .exceptions import CompilerError, InterpreterError, MWOTError


def mwot_to_bf(mwot):
    """Convert MWOT source to brainfuck."""
    return bytes(mwot_to_bf_chars(mwot))

def mwot_to_bf_chars(mwot):
    """Convert MWOT source to brainfuck instructions."""
    return brainfuck.from_bits(mwot_to_bits(mwot))

def mwot_to_binary(mwot):
    """Convert MWOT source to binary."""
    return bytes(mwot_to_binary_chars(mwot))

def mwot_to_binary_chars(mwot):
    """Convert MWOT source to binary bytes."""
    return bytes.from_bits(mwot_to_bits(mwot))
