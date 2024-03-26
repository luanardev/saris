class StudentNotFoundException(Exception):
    message = "Student profile not found"

    def __str__(self) -> str:
        return self.message