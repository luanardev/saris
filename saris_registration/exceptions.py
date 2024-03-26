class AlreadyRegisteredException(Exception):
    message = "Student already registered"

    def __str__(self) -> str:
        return self.message


class RegistrationNotFoundException(Exception):
    message = "Student has not registered"

    def __str__(self) -> str:
        return self.message


class FailAndWithdrawalException(Exception):
    message = "Academic result is FAIL AND WITHDRAWAL"

    def __str__(self) -> str:
        return self.message


class DeregistrationException(Exception):
    message = "Cannot delete courses with grades"
    
    def __str__(self) -> str:
        return self.message


class RepeatFeesNotFoundException(Exception):
    message = "Repeat course fee not configured"

    def __str__(self) -> str:
        return self.message


class SupplementaryFeesNotFoundException(Exception):
    message = "Supplementary fee not configured"

    def __str__(self) -> str:
        return self.message


class RegistrationPolicyNotFoundException(Exception):
    message = "Registration policy not configured"

    def __str__(self) -> str:
        return self.message
    