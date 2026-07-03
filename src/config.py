import os

class Config:
    """Central configuration for the Payment Service."""
    RETRY_MAX_ATTEMPTS = int(os.getenv("RETRY_MAX_ATTEMPTS", 3))
    RETRY_BACKOFF_MS = int(os.getenv("RETRY_BACKOFF_MS", 100))
    RETRY_MAX_DELAY_MS = int(os.getenv("RETRY_MAX_DELAY_MS", 2000))
    RETRY_JITTER_MS = int(os.getenv("RETRY_JITTER_MS", 50))
    
    # TTL for the idempotency cache
    IDEMPOTENCY_CACHE_TTL_SECONDS = int(os.getenv("IDEMPOTENCY_CACHE_TTL_SECONDS", 3600))
