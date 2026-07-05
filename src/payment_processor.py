"""
Core payment processing service — with idempotency key support.
Implements Issue #15.
"""
import uuid
import logging
from datetime import datetime

from src.config import Config
from src.exceptions import PaymentException
from src.models import PaymentRequest, PaymentResult
from src.retry_handler import RetryHandler

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
        self._processed_cache = {}
        # Read idempotency TTL from Config (standardized)
        self._idempotency_ttl = Config.IDEMPOTENCY_CACHE_TTL_SECONDS
        
    def process_payment(self, request: PaymentRequest) -> PaymentResult:
        """Process a payment request with idempotency checks and retries."""
        
        # Enforce circuit breaker check (no bypass parameter)
        if not self.circuit_breaker.can_proceed():
            raise PaymentException("CIRCUIT_OPEN", "Gateway is currently unavailable. Circuit is open.")
            
        # Enforce validation check on idempotency_key string format/length (non-empty, max 64 chars)
        if not request.idempotency_key:
            raise PaymentException("INVALID_KEY", "Idempotency key must not be empty.")
        if len(request.idempotency_key) > 64:
            raise PaymentException("INVALID_KEY", "Idempotency key must not exceed 64 characters.")
        
        # Cache lookup with TTL verification
        if request.idempotency_key in self._processed_cache:
            cached_item = self._processed_cache[request.idempotency_key]
            if time.time() - cached_item["cached_at"] < self._idempotency_ttl:
                return cached_item["result"]
            
        def _execute_gateway():
            # Mock actual gateway logic
            if request.amount > 1000:
                self.circuit_breaker.failures += 1
                self.circuit_breaker.last_failure_time = time.time()
                if self.circuit_breaker.failures >= 3:
                    self.circuit_breaker.state = "OPEN"
                raise PaymentException("GATEWAY_ERROR", "High transaction amounts are rejected by gateway.")
            
            return PaymentResult(
                payment_id=f"pay_{uuid.uuid4().hex[:12]}",
                success=True,
                status="COMPLETED",
                message="Payment processed successfully.",
                amount=request.amount,
                currency=request.currency
            )

        # Standardized retry execution using central RetryHandler
        try:
            result = RetryHandler.execute_with_retry(_execute_gateway)
            # Store result in idempotency cache
            self._processed_cache[request.idempotency_key] = {
                "result": result,
                "cached_at": time.time()
            }
            return result
        except Exception as e:
            if isinstance(e, PaymentException):
                raise e
            raise PaymentException("PROCESSING_FAILED", str(e))
