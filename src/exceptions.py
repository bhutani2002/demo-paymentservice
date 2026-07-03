"""
Custom exception hierarchy for demo-paymentservice.

TEAM RULE (TD-004, enforced since PR #11):
All service exceptions must subclass ServiceException and provide
error_code and user_message. Raw exceptions (ValueError, RuntimeError, etc.)
must NEVER propagate to callers. Violation is a merge blocker.
"""


class ServiceException(Exception):
    """Base exception for all service-layer errors."""

    def __init__(self, error_code: str, user_message: str, detail: str = ""):
        self.error_code = error_code
        self.user_message = user_message
        self.detail = detail
        super().__init__(f"[{error_code}] {user_message}")


class PaymentException(ServiceException):
    """Raised when a payment cannot be processed."""


class RetryExhaustedException(ServiceException):
    """Raised when all retry attempts are exhausted."""


class IdempotencyException(ServiceException):
    """Raised for idempotency key validation failures."""


class CircuitBreakerOpenException(ServiceException):
    """Raised when the circuit breaker is open."""


class RefundException(ServiceException):
    """Raised when a refund cannot be processed."""
