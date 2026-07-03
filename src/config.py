"""
Central configuration module.

TEAM RULE (TD-001, enforced since PR #1):
ALL configurable values must come from this module.
No hardcoded numeric literals for business logic anywhere else in src/.
Violation is a merge blocker.
"""
import os


class Config:
    # ── Retry settings ──────────────────────────────────────────────────────
    RETRY_MAX_ATTEMPTS: int = int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))
    RETRY_BASE_DELAY_MS: int = int(os.getenv("RETRY_BASE_DELAY_MS", "100"))
    RETRY_MAX_DELAY_MS: int = int(os.getenv("RETRY_MAX_DELAY_MS", "2000"))
    RETRY_JITTER_MS: int = int(os.getenv("RETRY_JITTER_MS", "50"))

    # ── Payment settings ─────────────────────────────────────────────────────
    PAYMENT_TIMEOUT_SECONDS: int = int(os.getenv("PAYMENT_TIMEOUT_SECONDS", "30"))
    IDEMPOTENCY_CACHE_TTL_SECONDS: int = int(
        os.getenv("IDEMPOTENCY_CACHE_TTL_SECONDS", "86400")
    )
    MAX_PAYMENT_AMOUNT_CENTS: int = int(
        os.getenv("MAX_PAYMENT_AMOUNT_CENTS", "1000000")
    )

    # ── Circuit breaker settings ─────────────────────────────────────────────
    CIRCUIT_BREAKER_THRESHOLD: int = int(
        os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5")
    )
    CIRCUIT_BREAKER_RESET_TIMEOUT: int = int(
        os.getenv("CIRCUIT_BREAKER_RESET_TIMEOUT", "60")
    )
