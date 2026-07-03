from src.exceptions import PaymentException
from src.models import PaymentResult

class RefundService:
    """Service to handle refund requests for payments."""
    def __init__(self):
        self._refund_registry = set()
        
    def issue_refund(self, payment: PaymentResult, reason: str) -> dict:
        """Issues a refund for a previously completed payment."""
        if not payment.success:
            raise PaymentException(error_code="INVALID_PAYMENT", user_message="Cannot refund a failed payment.")
            
        if payment.payment_id in self._refund_registry:
            raise PaymentException(error_code="ALREADY_REFUNDED", user_message="This payment has already been refunded.")
            
        self._refund_registry.add(payment.payment_id)
        return {
            "refund_id": f"ref_{payment.payment_id[4:]}",
            "status": "SUCCESS",
            "amount": payment.amount,
            "reason": reason
        }
