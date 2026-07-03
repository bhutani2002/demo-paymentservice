"""Tests for idempotency key support (Issue #15)."""
import pytest
from src.models import PaymentRequest, PaymentStatus
from src.payment_processor import PaymentProcessor
from src.exceptions import IdempotencyException


def make_request(**kwargs):
    defaults = dict(
        amount_cents=2000,
        currency="USD",
        merchant_id="merch_01",
        customer_id="cust_01",
        description="Idempotency test",
        idempotency_key="idem-test-001",
    )
    defaults.update(kwargs)
    return PaymentRequest(**defaults)


def test_idempotency_duplicate_returns_cached_result():
    """Criterion 2: duplicate requests return same result."""
    processor = PaymentProcessor()
    req = make_request(idempotency_key="unique-key-123")
    result1 = processor.process_payment(req)
    result2 = processor.process_payment(req)
    assert result1.payment_id == result2.payment_id


def test_empty_idempotency_key_raises():
    """Criterion 3 (partial): empty key is rejected."""
    processor = PaymentProcessor()
    with pytest.raises(IdempotencyException):
        processor.process_payment(make_request(idempotency_key=""))


# BUG 4 (Spec Gap — Criterion 6 PARTIAL):
# Missing test: idempotency_key over 64 chars should be rejected.
# Missing test: expired key allows re-processing.
# Criterion 6 requires BOTH scenarios to be tested.
