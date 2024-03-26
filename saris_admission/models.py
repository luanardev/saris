import uuid
from django.db import models
from saris.models import SarisModel
from saris_calendar.models import AcademicSemester, AcademicYear
from saris_curriculum.models import Program, IntakeType, ProgramLevel
from saris_institution.models import Campus
from saris_students.models import Student
from .exceptions import (
    EnrollmentNotFoundException, 
    EnrollmentNotActiveException,
    StudentNotAdmittableException,
    StudiesCompletedException, 
    StudentWithdrawnException,
    WithdrawalNotActiveException
)


class SponsorshipType(models.TextChoices):
    SELF = 'SELF'
    GRANT = 'GRANT'
    SCHOLARSHIP = 'SCHOLARSHIP'
    GOVERNMENT = 'GOVERNMENT'


class EnrollmentStatus(models.TextChoices):
    ENROLLED = 'ENROLLED'
    COMPLETED = 'COMPLETED'
    RESERVED = 'RESERVED'
    GRADUATED = 'GRADUATED'
    WITHDRAWAL = 'WITHDRAWAL'


class WithdrawalPeriod(models.TextChoices):
    ACADEMIC_SEMESTER= 'ACADEMIC SEMESTER'
    ACADEMIC_YEAR = 'ACADEMIC YEAR'
    INDEFINATE = 'INDEFINATE'
    

class WithdrawalStatus(models.TextChoices):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'


class WithdrawalType(SarisModel):
    ACADEMIC = "Academic"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    period = models.CharField(max_length=255, choices=WithdrawalPeriod.choices)

    class Meta:
        verbose_name = 'Withdrawal type'
        verbose_name_plural = 'withdrawal types'
    
    def __str__(self):
        return f"{self.name}"
    
    @staticmethod
    def get_by_name(name):
        object = WithdrawalType.objects.filter(name=name).first()
        if not object:
            raise Exception(f"Withdrawal type `{name}` not found")
        return object
    
    @staticmethod
    def get_academic():
        return WithdrawalType.get_by_name(WithdrawalType.ACADEMIC)
    
    
class Enrollment(SarisModel):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True, unique=True)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    program = models.ForeignKey(Program, on_delete=models.DO_NOTHING)
    campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.DO_NOTHING)
    semester = models.IntegerField(default=1)
    initial_semester = models.IntegerField(default=1)
    intake_type = models.CharField(max_length=255, choices=IntakeType.choices,  blank=True, null=True)
    sponsorship_type =  models.CharField(max_length=255, choices=SponsorshipType.choices, blank=True, null=True)
    status = models.CharField(max_length=255, choices=EnrollmentStatus.choices, default=EnrollmentStatus.ENROLLED, blank=True, null=True)
    is_compensated = models.BooleanField(blank=True, null=True, default=False)
    is_graduating = models.BooleanField(blank=True, null=True, default=False)
    is_certified = models.BooleanField(blank=True, null=True, default=False)
    award_name = models.CharField(max_length=255, blank=True, null=True)
    award_class = models.CharField(max_length=255, blank=True, null=True)
    award_level = models.CharField(max_length=255, choices=ProgramLevel.choices, blank=True, null=True)
    award_gpa = models.FloatField(blank=True, null=True)


    class Meta:
        verbose_name = 'Enrollment'
        verbose_name_plural = 'enrollments'
    
    def __str__(self):
        return f"{self.student.student_number}"
    
    def set_student(self, student):
        self.student = student

    def save(self, *args, **kwargs):
        if not self.pk:
            self.semester = self.initial_semester
        super(Enrollment, self).save(*args, **kwargs)

    def compensate(self):
        self.is_compensated = True

    def certify(self):
        self.is_certified = True

    def graduating(self):
        self.is_graduating = True

    def graduate(self):
        self.status = EnrollmentStatus.GRADUATED

    def activate(self):
        self.status = EnrollmentStatus.ENROLLED

    def complete(self):
        self.status = EnrollmentStatus.COMPLETED

    def withdrawal(self):
        self.status = EnrollmentStatus.WITHDRAWAL

    def reserve(self):
        self.status = EnrollmentStatus.RESERVED

    def check_withdrawal(self):
        if self.is_withdrawal():
            raise StudentWithdrawnException

    def check_completion(self):
        if self.is_completed() or self.is_graduated():
            raise StudiesCompletedException

    def is_enrolled(self) -> bool:
        return self.status == EnrollmentStatus.ENROLLED
    
    def is_withdrawal(self) -> bool:
        return self.status == EnrollmentStatus.WITHDRAWAL
        
    def is_completed(self) -> bool:
        return self.status == EnrollmentStatus.COMPLETED
    
    def is_graduated(self) -> bool:
        return self.status == EnrollmentStatus.GRADUATED

    @property
    def student_number(self):
        return self.student.student_number

    @staticmethod
    def get_active(student_number):
        enrollment = Enrollment.objects.filter(student__student_number=student_number).latest('created_at')
        if not enrollment:
            raise EnrollmentNotActiveException
        return enrollment

    @staticmethod
    def get_by_serial_number(serial_number):
        enrollment = Enrollment.objects.get(serial_number=serial_number)
        if not enrollment:
            raise EnrollmentNotFoundException
        return enrollment  


class Withdrawal(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.DO_NOTHING)
    academic_semester = models.ForeignKey(AcademicSemester, on_delete=models.DO_NOTHING)
    semester = models.IntegerField()
    withdrawal_type = models.ForeignKey(WithdrawalType, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=255, choices=WithdrawalStatus.choices, default=WithdrawalStatus.ACTIVE)

    class Meta:
        verbose_name = 'Withdrawal'
        verbose_name_plural = 'withdrawals'

    def activate(self):
        self.status = WithdrawalStatus.ACTIVE
    
    def deactivate(self):
        self.status = WithdrawalStatus.INACTIVE

    def check_readmittance(self):
        if self.is_not_active():
            raise WithdrawalNotActiveException
        if self.can_not_readmit():
            raise StudentNotAdmittableException

    def can_readmit(self):
        if self.withdrawal_type.period not in [WithdrawalPeriod.INDEFINATE]:
            return True
        else:
            return False

    def can_not_readmit(self):
        return not self.can_readmit()

    def is_active(self):
        if self.status == WithdrawalStatus.ACTIVE:
            return True
        else:
            return False
        
    def is_not_active(self):
        return not self.is_active()