"""
Core payment processing service — with idempotency key support.
Implements Issue #15.
"""
import uuid
import logging
from datetime import datetime

from src.config import Config
from src.exceptions import (
    CircuitBreakerOpenException,
    IdempotencyException,
    PaymentException,
)
from src.models import PaymentRequest, PaymentResult, PaymentStatus
from src.retry_handler import RetryHandler

logger = logging.getLogger(__name__)

SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP", "INR", "SGD"}


class CircuitBreaker:
    def __init__(self):
        self.failure_count: int = 0
        self.threshold: int = Config.CIRCUIT_BREAKER_THRESHOLD
        self.reset_timeout: int = Config.CIRCUIT_BREAKER_RESET_TIMEOUT
        self.is_open: bool = False
        self.opened_at: datetime | None = None

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.threshold:
            self.is_open = True
            self.opened_at = datetime.now()

    def record_success(self) -> None:
        self.failure_count = 0
        self.is_open = False

    def can_proceed(self) -> bool:
        if not self.is_open:
            return True
        elapsed = (datetime.now() - self.opened_at).seconds
        if elapsed >= self.reset_timeout:
            self.is_open = False
            self.failure_count = 0
            return True
        return False


class PaymentProcessor:
    def __init__(self):
        self.retry_handler = RetryHandler()
        self.circuit_breaker = CircuitBreaker()
        self._processed_cache: dict[str, dict] = {}
        # BUG 1: Hardcoded TTL — should be Config.IDEMPOTENCY_CACHE_TTL_SECONDS (TD-001, TD-006)
        self._idempotency_ttl = 86400

    def _validate_idempotency_key(self, key: str) -> None:
        """
        Validate idempotency key.
        BUG 3: Acceptance criterion 3 requires: non-empty string, max 64 chars.
        This implementation only checks for empty string — does NOT enforce max 64 chars.
        """
        if not key:
            raise IdempotencyException(
                error_code="INVALID_IDEMPOTENCY_KEY",
                user_message="Idempotency key must not be empty.",
            )
        # MISSING: if len(key) > 64: raise IdempotencyException(...)

    def process_payment(self, request: PaymentRequest) -> PaymentResult:
        self._validate_idempotency_key(request.idempotency_key)

        if request.idempotency_key in self._processed_cache:
            logger.info("Returning cached result for key=%s", request.idempotency_key)
            cached = self._processed_cache[request.idempotency_key]
            return cached["result"]

        if not self.circuit_breaker.can_proceed():
            raise CircuitBreakerOpenException(
                error_code="CIRCUIT_OPEN",
                user_message="Payment service temporarily unavailable.",
            )

        self._validate(request)

        try:
            result = self._process_with_custom_retry(request)
            self.circuit_breaker.record_success()
        except Exception:
            self.circuit_breaker.record_failure()
            raise

        self._processed_cache[request.idempotency_key] = {
            "result": result,
            "cached_at": datetime.now(),
        }
        return result

    def _process_with_custom_retry(self, request: PaymentRequest) -> PaymentResult:
        """
        BUG 2: Hardcoded max_attempts = 5 instead of using RetryHandler / Config.
        Team standard is 3 (TD-002). This also bypasses RetryHandler entirely.
        """
        max_attempts = 5  # WRONG — must be Config.RETRY_MAX_ATTEMPTS via RetryHandler
        last_exc = None
        for attempt in range(max_attempts):
            try:
                return self._call_payment_gateway(request)
            except Exception as exc:
                last_exc = exc
                logger.warning("Attempt %d failed: %s", attempt + 1, exc)
        raise PaymentException(
            error_code="PAYMENT_FAILED",
            user_message="Payment could not be processed after multiple attempts.",
            detail=str(last_exc),
        )

    def _validate(self, request: PaymentRequest) -> None:
        if request.amount_cents <= 0:
            raise PaymentException(
                error_code="INVALID_AMOUNT",
                user_message="Payment amount must be positive.",
            )
        if request.amount_cents > Config.MAX_PAYMENT_AMOUNT_CENTS:
            raise PaymentException(
                error_code="AMOUNT_EXCEEDS_LIMIT",
                user_message="Payment amount exceeds maximum allowed.",
            )
        if request.currency not in SUPPORTED_CURRENCIES:
            raise PaymentException(
                error_code="UNSUPPORTED_CURRENCY",
                user_message=f"Currency {request.currency!r} is not supported.",
            )

    def _call_payment_gateway(self, request: PaymentRequest) -> PaymentResult:
        return PaymentResult(
            payment_id=str(uuid.uuid4()),
            status=PaymentStatus.COMPLETED,
            amount_cents=request.amount_cents,
            currency=request.currency,
            timestamp=datetime.now(),
            idempotency_key=request.idempotency_key,
        )
