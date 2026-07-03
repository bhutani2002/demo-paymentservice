import pytest
import time
from src.retry_handler import RetryHandler
from src.exceptions import ServiceException

def test_retry_handler_success_after_failure():
    call_count = 0
    
    def failing_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Temporary failure")
        return "success"
        
    res = RetryHandler.execute_with_retry(failing_func)
    assert res == "success"
    assert call_count == 2

def test_retry_handler_raises_after_max_attempts():
    call_count = 0
    
    def constant_failure():
        nonlocal call_count
        call_count += 1
        raise ValueError("Constant failure")
        
    with pytest.raises(ValueError):
        RetryHandler.execute_with_retry(constant_failure)
    assert call_count == 3  # Config.RETRY_MAX_ATTEMPTS is 3
