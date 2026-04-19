class ApiError(Exception):
    """Raised when the API returns a non-200 status in the JSON body."""

    def __init__(self, status: int, body: object) -> None:
        self.status = status
        self.body = body
        super().__init__(f"API returned status {status}")


class BankidStop(Exception):
    """Raised when the BankID flow is aborted by the backend."""


class NotLoggedInError(Exception):
    """Raised when a privileged endpoint is called before BankID succeeds."""


class LicenceNotFoundError(LookupError):
    """Raised by lookup helpers when no matching licence exists."""
