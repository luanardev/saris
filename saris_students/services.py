from datetime import date
from saris.utils import add_years
from account.services import Signatory
from saris_students.models import Student
from saris_students.apps import SarisStudentsConfig


APP_NAME = SarisStudentsConfig.name


class IDCard(object):

    def __init__(self, student: Student) -> None:
        self.student = student
        self.signatory = Signatory.university_registrar()
        self.issue_date = date.today()
        self.expire_date = add_years(self.issue_date, 5)
        self.qrcode_info = self._get_qrcode_info()

        if not student.user.passport_photo:
            raise Exception("Student passport photo not found")
        if not student.user.signature:
            raise Exception("Student signature not foud")

    def _get_qrcode_info(self):
        data = f'''
            StudentNumber: {self.student.student_number}, 
            FirstName: {self.student.first_name},
            LastName: {self.student.last_name},
            Gender: {self.student.gender},
            Programme: {self.student.enrollment.program.code}
        '''
        return data
        

class StudentAppeal(object):

    def __init__(self, student_number, appeal_type) -> None:
        self.student_number = student_number
        self.appeal_type = appeal_type
        self.appeal_courses= list()


    def set_course(self, appeal_course):
        self.appeal_courses.append(appeal_course)

    def set_courses(self, appeal_courses):
        for appeal_course in appeal_courses:
            if appeal_course not in self.appeal_courses:
                self.set_course(appeal_course)