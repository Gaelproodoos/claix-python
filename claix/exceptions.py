"""Typed exceptions for the Claix Python SDK."""

from __future__ import annotations

from typing import Any


class ClaixError(Exception):
    """Base error for every Claix SDK failure."""

    def __init__(self, message: str, *, status_code: int | None = None, payload: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload


class ClaixAuthenticationError(ClaixError):
    """Missing, invalid, inactive, or unauthorized API key (HTTP 401)."""


class ClaixNotFoundError(ClaixError):
    """Resource does not exist, does not belong to the account, or has expired (HTTP 404)."""


class ClaixValidationError(ClaixError):
    """Invalid request parameters or unmapped schema fields (HTTP 400 / 413 / 422)."""


class ClaixRateLimitError(ClaixError):
    """Too many requests (HTTP 429). ``retry_after`` is seconds when present."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = 429,
        payload: Any = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, payload=payload)
        self.retry_after = retry_after


class ClaixTimeoutError(ClaixError):
    """The HTTP call exceeded the configured timeout."""


class ClaixConnectionError(ClaixError):
    """Network-level failure talking to Claix."""


class ClaixAPIError(ClaixError):
    """Unexpected API failure (HTTP 5xx or an unclassified status)."""
