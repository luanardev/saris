
class InsufficientFundsException(Exception):
    message = "Student has insufficient funds"
    def __str__(self) -> str:
        return self.message


class InvoiceNotFoundException(Exception):
    message = "Invoice not found"
    def __str__(self) -> str:
        return self.message
    

class InvoiceExistsException(Exception):
    message = "Invoice already exists"
    def __str__(self) -> str:
        return self.message


class OverPaymentException(Exception):
    message = "Payment exceeds required amount"

    def __str__(self) -> str:
        return self.message


class UnderPaymentException(Exception):
    message = "Payment fails to meet required amount"

    def __str__(self) -> str:
        return self.message


class InvoiceAlreadySettledException(Exception):
    message = "Invoice already settled"

    def __str__(self) -> str:
        return self.message


class BankDetailsNotFoundException(Exception):
    message = "Bank account not configured"

    def __str__(self) -> str:
        return self.message


class TuitionDetailsNotFoundException(Exception):
    message = "Tuition fee not configured"

    def __str__(self) -> str:
        return self.message
    
    
class ServiceFeeNotFoundException(Exception):
    message = "Service fee not configured"

    def __str__(self) -> str:
        return self.message


class BalanceException(Exception):
    message = "You have outstanding balance"

    def __str__(self) -> str:
        return self.message
    
    
class NoBalanceException(Exception):
    message = "No outstanding balance"

    def __str__(self) -> str:
        return self.message