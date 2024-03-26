class EnrollmentNotFoundException(Exception):
    message = "Enrollment not found"

    def __str__(self) -> str:
        return self.message

class EnrollmentNotActiveException(Exception):
    message = "Enrollment not active"

    def __str__(self) -> str:
        return self.message
    

class StudentWithdrawnException(Exception):
    message = "Student withdrawn from studies"

    def __str__(self) -> str:
        return self.message
    

class StudiesCompletedException(Exception):
    message = "Student completed studies"

    def __str__(self) -> str:
        return self.message


class WithdrawalNotActiveException(Exception):
    message = "Student withdrawal not active"

    def __str__(self) -> str:
        return self.message


class StudentNotAdmittableException(Exception):
    message = "Student not admittable"

    def __str__(self) -> str:
        return self.message
