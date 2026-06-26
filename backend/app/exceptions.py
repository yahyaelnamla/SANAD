"""Application-specific exceptions for SANAD API."""

from typing import Any


class SANADError(Exception):
    """Base exception for SANAD application errors."""

    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(SANADError):
    """Resource not found."""

    status_code = 404
    code = "NOT_FOUND"


class ForbiddenError(SANADError):
    """Insufficient permissions."""

    status_code = 403
    code = "FORBIDDEN"


class ValidationError(SANADError):
    """Invalid request data."""

    status_code = 400
    code = "VALIDATION_ERROR"


class NoEvidenceError(SANADError):
    """No authenticated sources found — No Hallucination Policy."""

    status_code = 422
    code = "NO_EVIDENCE"


class UnauthorizedError(SANADError):
    """Missing or invalid authentication."""

    status_code = 401
    code = "UNAUTHORIZED"
