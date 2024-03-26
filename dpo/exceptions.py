
class FailedToCreateToken(Exception):
    message = "Failed to Create Token"

    def __str__(self) -> str:
        return self.message
    

class FailedToCancelToken(Exception):
    message = "Failed to Cancel Token"

    def __str__(self) -> str:
        return self.message
    

class FailedToVerifyToken(Exception):
    message = "Transaction Not Paid"

    def __str__(self) -> str:
        return self.message
    

class FailedToRefundToken(Exception):
    message = "Failed to Refund Token"

    def __str__(self) -> str:
        return self.message