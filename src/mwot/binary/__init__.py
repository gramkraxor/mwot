"""Binary (bytes) language: conversions between bytes and MWOT bits."""

from ..join import joinable
from .. import stypes
from ..util import chunk_bits

bitrange = range(8)[::-1]


@joinable(bytes)
def from_bits(bits):
    """Yield bytes from MWOT bits."""
    for chunk in chunk_bits(bits, chunk_size=8):
        yield sum(b << i for i, b in zip(bitrange, chunk))


@joinable()
def to_bits(chars):
    """Convert bytes to MWOT bits."""
    stype, chars = stypes.probe(chars, default=stypes.Bytes)
    if stype is not stypes.Bytes:
        raise TypeError('chars must be bytes')
    for byte in chars:
        for i in bitrange:
            yield (byte >> i) & 1
