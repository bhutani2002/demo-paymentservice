import pytest
from src.models import PaymentRequest
from src.exceptions import PaymentException
from src.payment_processor import PaymentProcessor

def test_idempotency_duplicate_returns_cached_result():
    processor = PaymentProcessor()
    req = PaymentRequest(
        amount=100.0,
        currency="USD",
        card_number="1234-5678-9012-3456",
        expiry="12/28",
        cvv="123",
        idempotency_key="key_12345"
    )
    
    # First process
    res1 = processor.process_payment(req)
    assert res1.success is True
    assert res1.status == "COMPLETED"
    
    # Second process with same key (should return cached response)
    res2 = processor.process_payment(req)
    assert res2.payment_id == res1.payment_id
    assert res2.success is True

def test_circuit_breaker_blocks_when_open():
    processor = PaymentProcessor()
    req = PaymentRequest(
        amount=1500.0,  # Trigger failures (> 1000)
        currency="USD",
        card_number="1234-5678-9012-3456",
        expiry="12/28",
        cvv="123"
    )
    
    # Trigger 3 failures to open circuit
    for _ in range(3):
        try:
            processor.process_payment(req)
        except PaymentException:
            pass
            
    assert processor.circuit_breaker.state == "OPEN"
    
    # 4th request should fail immediately with CIRCUIT_OPEN
    with pytest.raises(PaymentException) as excinfo:
        req2 = PaymentRequest(amount=50.0, currency="USD", card_number="1234", expiry="12", cvv="1")
        processor.process_payment(req2)
    assert excinfo.value.error_code == "CIRCUIT_OPEN"

def test_idempotency_key_length_validation():
    processor = PaymentProcessor()
    # Key exceeds 64 characters
    long_key = "x" * 65
    req = PaymentRequest(
        amount=100.0,
        currency="USD",
        card_number="1234-5678-9012-3456",
        expiry="12/28",
        cvv="123",
        idempotency_key=long_key
    )
    with pytest.raises(PaymentException) as excinfo:
        processor.process_payment(req)
    assert excinfo.value.error_code == "INVALID_KEY"
