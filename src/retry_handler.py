import time
import random
from src.config import Config

class RetryHandler:
    """Centralized retry handler with exponential backoff and random jitter."""
    
    @staticmethod
    def execute_with_retry(func, *args, **kwargs):
        attempts = 0
        max_attempts = Config.RETRY_MAX_ATTEMPTS  # Standardized to 3 (TD-002)
        
        while attempts < max_attempts:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempts += 1
                if attempts >= max_attempts:
                    raise e
                
                # Calculate exponential delay
                delay_ms = Config.RETRY_BACKOFF_MS * (2 ** (attempts - 1))
                delay_ms = min(delay_ms, Config.RETRY_MAX_DELAY_MS)
                
                # Add random jitter (Issue #16)
                jitter = random.randint(0, Config.RETRY_JITTER_MS)
                total_delay_sec = (delay_ms + jitter) / 1000.0
                
                time.sleep(total_delay_sec)
