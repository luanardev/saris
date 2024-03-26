
class AcademicSemesterNotFoundException(Exception):
    message = "Academic semester not configured"

    def __str__(self) -> str:
        return self.message