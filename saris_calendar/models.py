import uuid
from django.db import models
from saris.models import SarisModel
from saris_institution.models import Campus
from .exceptions import AcademicSemesterNotFoundException


class StatusType(models.TextChoices):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'


class AcademicYear(SarisModel):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=20)
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    status = models.CharField(max_length=255, choices=StatusType.choices)

    class Meta:
        verbose_name = 'Academic Year'
        verbose_name_plural = 'academic years'
        ordering = ['-start_year']

    def __str__(self):
        return self.code


class AcademicActivity(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Academic Activity'
        verbose_name_plural = 'academic activities'

    def __str__(self):
        return self.name


class AcademicSemester(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    semester = models.IntegerField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=255, choices=StatusType.choices)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.DO_NOTHING)
    campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING)
    activities = models.ManyToManyField(AcademicActivity, through='AcademicSemesterActivity')

    class Meta:
        verbose_name = 'Academic Semester'
        verbose_name_plural = 'academic semesters'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    
    @staticmethod
    def has_active(campus: Campus):
        status = StatusType.ACTIVE
        return AcademicSemester.objects.filter(campus=campus, status=status).exists()
    
    @staticmethod
    def get_active(campus: Campus):
        status = StatusType.ACTIVE
        academic_semester = AcademicSemester.objects.filter(campus=campus, status=status).first()
        if not academic_semester:
            raise AcademicSemesterNotFoundException
        return academic_semester
    
    @staticmethod
    def get_previous(campus: Campus):
        try:
            academic_semester = AcademicSemester.objects.filter(campus=campus).order_by('-created_at')[1]
            return academic_semester
        except:
            raise AcademicSemesterNotFoundException


class AcademicSemesterActivity(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=255, choices=StatusType.choices)
    academic_semester = models.ForeignKey(AcademicSemester, on_delete=models.CASCADE)
    academic_activity = models.ForeignKey(AcademicActivity, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Academic Semester Activity'
        verbose_name_plural = 'academic semesters activities'

        
           