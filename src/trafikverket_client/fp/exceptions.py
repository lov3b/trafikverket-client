class BankidStop(Exception):
    """Raised when the BankID flow is aborted by the backend."""


class NotLoggedInError(Exception):
    """Raised when a privileged endpoint is called before BankID succeeds."""


class LicenceNotFoundError(LookupError):
    """Raised by lookup helpers when no matching licence exists."""
