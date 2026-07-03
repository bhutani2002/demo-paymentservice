import pytest
from src.models import PaymentResult
from src.exceptions import PaymentException
from src.refund_service import RefundService

def test_refund_success():
    service = RefundService()
    payment = PaymentResult(
        payment_id="pay_12345",
        success=True,
        status="COMPLETED",
        message="Ok",
        amount=50.0,
        currency="USD"
    )
    
    res = service.issue_refund(payment, "Customer request")
    assert res["status"] == "SUCCESS"
    assert res["amount"] == 50.0

def test_refund_already_refunded_raises():
    service = RefundService()
    payment = PaymentResult(
        payment_id="pay_12345",
        success=True,
        status="COMPLETED",
        message="Ok",
        amount=50.0,
        currency="USD"
    )
    
    service.issue_refund(payment, "First time")
    with pytest.raises(PaymentException) as excinfo:
        service.issue_refund(payment, "Second time")
    assert excinfo.value.error_code == "ALREADY_REFUNDED"
