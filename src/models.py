import uuid
from dataclasses import dataclass, field

@dataclass
class PaymentRequest:
    """Payment request details."""
    amount: float
    currency: str
    card_number: str
    expiry: str
    cvv: str
    # Generate automatic UUID if no idempotency key is provided
    idempotency_key: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class PaymentResult:
    """Payment processing result."""
    payment_id: str
    success: bool
    status: str
    message: str
    amount: float
    currency: str
