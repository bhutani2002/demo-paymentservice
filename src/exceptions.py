class ServiceException(Exception):
    """Base exception for all payment service operations."""
    def __init__(self, error_code: str, user_message: str):
        self.error_code = error_code
        self.user_message = user_message
        super().__init__(f"[{error_code}] {user_message}")

class PaymentException(ServiceException):
    """Exception specifically for payment operations."""
    pass
