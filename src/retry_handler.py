"""
Retry handler with exponential backoff and jitter.

TEAM STANDARD (TD-002, PR #3):
  - Max attempts: Config.RETRY_MAX_ATTEMPTS (currently 3)
  - Backoff: exponential starting at Config.RETRY_BASE_DELAY_MS
  - Jitter: Config.RETRY_JITTER_MS added randomly per attempt
  - Max delay: Config.RETRY_MAX_DELAY_MS

Do NOT set custom attempt counts inline. Use Config.
"""
import random
import time
import logging

from src.config import Config
from src.exceptions import RetryExhaustedException

logger = logging.getLogger(__name__)


class RetryHandler:
    def __init__(self):
        self.max_attempts = Config.RETRY_MAX_ATTEMPTS
        self.base_delay_ms = Config.RETRY_BASE_DELAY_MS
        self.max_delay_ms = Config.RETRY_MAX_DELAY_MS
        self.jitter_ms = Config.RETRY_JITTER_MS

    def execute_with_retry(self, func, *args, **kwargs):
        """
        Execute `func` with exponential backoff retry.
        Raises RetryExhaustedException if all attempts fail.
        """
        last_exception = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                logger.info("Attempt %d/%d", attempt, self.max_attempts)
                return func(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001
                last_exception = exc
                if attempt == self.max_attempts:
                    break
                delay = self._compute_delay(attempt)
                logger.warning(
                    "Attempt %d failed: %s. Retrying in %dms", attempt, exc, delay
                )
                time.sleep(delay / 1000)

        raise RetryExhaustedException(
            error_code="RETRY_EXHAUSTED",
            user_message="Service temporarily unavailable. Please try again later.",
            detail=str(last_exception),
        )

    def _compute_delay(self, attempt: int) -> int:
        """Exponential backoff with random jitter."""
        base = self.base_delay_ms * (2 ** (attempt - 1))
        jitter = random.randint(0, self.jitter_ms)
        return min(base + jitter, self.max_delay_ms)
