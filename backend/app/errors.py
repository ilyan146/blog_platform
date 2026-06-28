"""Domain errors raised by services and mapped to HTTP responses in main.py.

Keeping these HTTP-free lets services stay testable without FastAPI.
"""


class AppError(Exception):
    """Base application error. `status_code` drives the HTTP response."""

    status_code = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class AuthError(AppError):
    status_code = 401


class ConflictStateError(AppError):
    """The resource exists but is in the wrong state for this action."""

    status_code = 409
