import uuid
from django.db import models
from saris.models import SarisModel
from saris_institution.models import Department
from saris_calendar.models import AcademicSemester


class StatusType(models.TextChoices):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'


class CourseType(models.TextChoices):
    CORE = 'CORE'
    NONCORE = 'NONCORE' 
    ELECTIVE = 'ELECTIVE'
    AUDIT = 'AUDIT'


class IntakeType(models.TextChoices):
    GENERIC = 'GENERIC'
    MATURE = 'MATURE'


class ProgramType(models.TextChoices):
    UNDERGRADUATE = 'UNDERGRADUATE'
    POSTGRADUATE = 'POSTGRADUATE'


class ProgramLevel(models.TextChoices):
    SHORTCOURSE = 'SHORTCOURSE'
    CERTIFICATE = 'CERTIFICATE'
    DIPLOMA = 'DIPLOMA'
    BACHELORS = 'BACHELORS'
    HONOURS = 'HONOURS'
    PG_CERTIFICATE = 'PG_CERTIFICATE'
    PG_DIPLOMA = 'PG_DIPLOMA'
    MASTERS = 'MASTERS'
    DOCTORATE = 'DOCTORATE'


class Program(SarisModel):
    MULTIPLIER = 1.5

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    field_name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    years = models.IntegerField(default=4)
    semesters = models.IntegerField(default=8)
    max_semesters = models.IntegerField(blank=True, null=True)
    min_credit_hours = models.FloatField(blank=True, null=True)
    max_credit_hours = models.FloatField(blank=True, null=True)
    program_type = models.CharField(max_length=255, choices=ProgramType.choices, blank=True, null=True)
    program_level = models.CharField(max_length=255, choices=ProgramLevel.choices, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=255, choices=StatusType.choices, default=StatusType.ACTIVE, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
   
    class Meta:
        verbose_name = 'Program'
        verbose_name_plural = 'programs'
        ordering = ['code']

    def save(self) -> None:
        self.max_semesters = self.semesters * self.MULTIPLIER
        return super().save()
    
    def get_courses(self):
        from .models import MasterCurriculum
        courses = MasterCurriculum.objects.filter(program=self)
        return courses  
    
    def get_courses_by_semester(self, semester):
        from .models import MasterCurriculum
        courses = MasterCurriculum.objects.filter(program=self, semester=semester)
        return courses   
          
    def get_semester_list(self):
        semesters = []
        for semester in range(1, self.semesters+1):
            semesters.append(semester)
        return semesters
    
    def has_courses(self):
        from .models import MasterCurriculum
        count = MasterCurriculum.objects.filter(program=self).count()
        if count > 0:
            return True
        else:
            return False
        
    def __str__(self):
        return self.name


class Course(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    credit_hours = models.FloatField()
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=255, choices=StatusType.choices, default=StatusType.ACTIVE, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'courses'
        ordering = ['code']

    def __str__(self):
        return self.name


class MasterCurriculum(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    program = models.ForeignKey(Program, on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    course_type = models.CharField(max_length=255, choices=CourseType.choices, blank=True, null=True)
    semester = models.IntegerField()
    version = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Master Curriculum'
        verbose_name_plural = 'master curriculum'
        ordering = ['course__code']
    
    def __str__(self) -> str:
        return self.course.name


class ConfiguredCurriculum(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    academic_semester = models.ForeignKey(AcademicSemester, on_delete=models.DO_NOTHING)
    program = models.ForeignKey(Program, on_delete=models.DO_NOTHING)
    semester = models.IntegerField()
    version = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Configured Curriculum'
        verbose_name_plural = 'configured curriculum'
        
    def courses(self):
        from .models import ConfiguredCourse
        courses = ConfiguredCourse.objects.filter(curriculum=self)
        return courses
    
    def __str__(self):
        return self.program.name


class ConfiguredCourse(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    curriculum = models.ForeignKey(ConfiguredCurriculum, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    course_type = models.CharField(max_length=255, choices=CourseType.choices, blank=True, null=True)
    semester = models.IntegerField()
    
    class Meta:
        verbose_name = 'Configured courses'
        verbose_name_plural = 'configured courses'
        ordering = ['course__code']
        
    def __str__(self) -> str:
        return self.course.name


        
        