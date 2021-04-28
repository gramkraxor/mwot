class MWOTError(Exception):
    """MWOT base error."""

class CompilerError(MWOTError):
    """Error while transpiling."""

class InterpreterError(MWOTError):
    """Error while running code."""
