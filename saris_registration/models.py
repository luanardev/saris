import uuid
from django.db import models
from saris.models import SarisModel
from saris_calendar.models import AcademicSemester
from saris_admission.models import Enrollment
from saris_institution.models import Campus
from saris_registration.exceptions import RegistrationPolicyNotFoundException


class RegistrationStatus(models.TextChoices):
    REGISTERED = 'REGISTERED'
    WITHDRAWAL = 'WITHDRAWAL'    


class RegistrationType(models.TextChoices): 
    NORMAL = 'NORMAL'
    REPEAT = 'REPEAT'
    SUP = 'SUP'


class Registration(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.DO_NOTHING)
    academic_semester = models.ForeignKey(AcademicSemester, on_delete=models.DO_NOTHING)
    semester = models.IntegerField()
    type = models.CharField(max_length=255, choices=RegistrationType.choices, default=RegistrationType.NORMAL)
    status = models.CharField(max_length=255, choices=RegistrationStatus.choices, default=RegistrationStatus.REGISTERED)

    class Meta:
        verbose_name = 'Registration'
        verbose_name_plural = 'registration'
        ordering = ['-created_at']
        
    def is_normal(self):
        if self.type == RegistrationType.NORMAL:
            return True
        else:
            return False
        
    def is_repeat(self):
        if self.type == RegistrationType.REPEAT:
            return True
        else:
            return False
     
    def is_sup(self):
        if self.type == RegistrationType.SUP:
            return True
        else:
            return False
        
    def withdrawal(self):
        self.status = RegistrationStatus.WITHDRAWAL

    def get_courses(self):
        from saris_assessment.models import StudentCourse
        courses = StudentCourse.objects.filter(
            enrollment=self.enrollment,
            academic_semester=self.academic_semester,
            semester=self.semester
        )
        return courses
    
    def delete_courses(self):
        from saris_assessment.models import StudentCourse
        StudentCourse.objects.filter(
            enrollment=self.enrollment,
            academic_semester=self.academic_semester,
            semester=self.semester
        ).delete()

    def count_graded_courses(self):
        from saris_assessment.models import StudentCourse
        count = StudentCourse.objects.filter(
            academic_semester=self.academic_semester,
            enrollment=self.enrollment,
            semester=self.semester
        ).exclude(
            final_grade=None,
            grade_point=None,
            letter_grade=None
        ).count()
        return count

    def has_graded_courses(self):
        count = self.count_graded_courses()
        if count > 0:
            return True
        else:
            return False
    
    def __str__(self):
        return self.enrollment.student.name


class RegistrationPolicy(SarisModel):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING)
    registration_installment = models.FloatField(blank=True, null=True)
    examination_installment = models.FloatField(blank=True, null=True)
    results_installment = models.FloatField(blank=True, null=True)
    block_registration = models.BooleanField(default=True)
    block_examination = models.BooleanField(default=True)
    block_results = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Registration Policy'
        verbose_name_plural = 'registration policies'

    def __str__(self) -> str:
        return f"{self.campus.name}"

    @staticmethod
    def get_by_campus(campus):
        policy = RegistrationPolicy.objects.filter(campus=campus).first()
        if not policy:
            raise RegistrationPolicyNotFoundException
        return policy

 