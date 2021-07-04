from ..exceptions import MWOTError


class CLIError(MWOTError):
    """Base error for the MWOT CLI."""

class OutfileFormatError(CLIError):
    """Error with the -o pattern."""
