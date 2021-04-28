class MWOTError(Exception):
    """MWOT base error."""

class CompilerError(MWOTError):
    """Error while transpiling."""
