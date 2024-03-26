
from account.services import Signatory, UserAccount
from saris_billing.services import TuitionManager
from saris_calendar.models import AcademicSemester
from saris_registration.models import Registration
from saris_students.models import Student
from .models import Enrollment, Withdrawal


class StudentEnrollment(object):

    def __init__(self, student, enrollment) -> None:
        if isinstance(student, Student):
            self.student = student
        else:
            raise ValueError

        if isinstance(enrollment, Enrollment):
            self.enrollment = enrollment
        else:
            raise ValueError

    def process(self):

        user_account = UserAccount(self.student.first_name, self.student.last_name, self.student.email_address)
        user = user_account.create_student()

        self.student.set_user(user)
        self.student.set_student_number()
        self.student.set_default_passcode()
        self.student.save()

        user.set_username(self.student.student_number)
        user.set_password(self.student.passcode)
        user.save()
        
        self.enrollment.set_student(self.student)
        self.enrollment.save()


class StudentWithdrawal(object):

    def __init__(self, student_number, withdrawal_type):
        self.student_number = student_number
        self.withdrawal_type = withdrawal_type
        self.enrollment = Enrollment.get_active(student_number)
        self.academic_semester = AcademicSemester.get_active(self.enrollment.campus)
        self.enrollment.check_withdrawal()
        self.enrollment.check_completion()


    def _get_registration(self):
        return Registration.objects.filter(
            enrollment=self.enrollment,
            academic_semester=self.academic_semester,
            semester=self.enrollment.semester
        ).first()

    def _withdrawal_enrollment(self):
        if self.enrollment.is_enrolled():
            self.enrollment.withdrawal()
            self.enrollment.save()

    def _withdrawal_registration(self):
        try:
            registration = self._get_registration()
            registration.withdrawal()
            registration.save()
        except:
            pass

    def _withdrawal(self):
        withdrawal = Withdrawal()
        withdrawal.enrollment = self.enrollment
        withdrawal.academic_semester = self.academic_semester
        withdrawal.semester = self.enrollment.semester
        withdrawal.withdrawal_type = self.withdrawal_type
        withdrawal.activate()
        withdrawal.save()
        return withdrawal

    def process(self):
        withdrawal = self._withdrawal()
        self._withdrawal_enrollment()
        self._withdrawal_registration()
        return withdrawal

        
class StudentReadmission(object):
    
    def __init__(self, withdrawal):
        if isinstance(withdrawal, Withdrawal):
            self.withdrawal = withdrawal
        else:
            self.withdrawal = Withdrawal.get_by_id(withdrawal)

        self.enrollment = self.withdrawal.enrollment
        self.enrollment.check_completion()

    def _activate_enrollment(self):
        if self.enrollment.is_withdrawal():
            self.enrollment.activate()
            self.enrollment.save()

    def _deactivate_withdrawal(self):
        self.withdrawal.check_readmittance()
        self.withdrawal.deactivate()
        self.withdrawal.save()

    def process(self):
        self._activate_enrollment()
        self._deactivate_withdrawal()
        return self.withdrawal
        

class AdmissionLetter(object):

    def __init__(self, enrollment) -> None:
        if isinstance(enrollment, Enrollment):
            self.enrollment = enrollment
        else:
            self.enrollment = Enrollment.get_by_id(enrollment)

        self.signatory = Signatory.university_registrar()

        manager = TuitionManager(self.enrollment)
        self.tuition = manager.get_tuition_fee()
        self.bank = manager.get_bank_account()
        

class AdmissionLetters(object):

    def __init__(self, enrollments) -> None:
        self.enrollments = enrollments

    def get_letters(self):
        letters = list()
        for enrollment in self.enrollments:
            letter = AdmissionLetter(enrollment)
            letters.append(letter)
        return letters