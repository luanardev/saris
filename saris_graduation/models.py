import uuid
from django.db import models
from saris.models import SarisModel, WorkMixin, WorkStatus
from saris.utils import get_file_path
from saris_graduation.apps import SarisGraduationConfig
from saris_admission.models import Enrollment
from saris_calendar.models import AcademicYear


APP_NAME = SarisGraduationConfig.name


class Session(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.DO_NOTHING)
    graduation_date = models.DateField()

    class Meta:
        verbose_name = 'Session'
        verbose_name_plural = 'sessions'
    
    def __str__(self):
        return f"{self.name}"

    @staticmethod
    def get_current():
        return Session.objects.latest('created_at')


class Candidate(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.DO_NOTHING)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = 'Candidate'
        verbose_name_plural = 'candidates'
        ordering = ['-enrollment__award_gpa']
    
    def __str__(self):
        return f"{self.enrollment.student.student_number}"
   

class Booklet(WorkMixin, SarisModel):
    FILE_UPLOAD = get_file_path("booklet", APP_NAME)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=45, choices=WorkStatus.choices, default=WorkStatus.PENDING)
    error = models.CharField(max_length=255, blank=True, null=True)
    pdf_file = models.FileField(upload_to=FILE_UPLOAD, null=True, blank=True)

    class Meta:
        verbose_name = 'Booklet'
        verbose_name_plural = 'booklets'

    def __str__(self):
        return f"{self.session.name}"
    