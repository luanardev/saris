
from saris_students.models import Student

class StudentMixin:
    
    def get_student(self, **kwargs) -> Student:
        student = self.request.user.student
        return student