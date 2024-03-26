import uuid
from django.db import models
from saris.models import SarisModel, WorkMixin, WorkStatus
from saris.utils import get_file_path
from account.models import Staff
from saris_admission.models import Enrollment
from saris_calendar.models import AcademicSemester
from saris_curriculum.models import Course, CourseType, ProgramLevel, ProgramType
from saris_institution.models import Faculty
from saris_assessment.apps import SarisAssessmentConfig
from .exceptions import (
    AssessmentVersionNotFoundException, 
    GradeBenchMarkNotFoundException, 
    GradeSchemeVersionNotFoundException,
    PassMarkNotFoundException
)

APP_NAME = SarisAssessmentConfig.name


class ResultDescription(models.TextChoices):
    PAP = 'PASS'
    PCO = 'PASS WITH CARRYOVER'
    RFC = 'REPEAT FAILED COURSE'
    FAW = 'FAIL AND WITHDRAWAL'
    SUP = 'SUPPLEMENTARY'
    MGD = 'MISSING GRADE'
    SAW = 'SERIOUS WARNING'
    SUP_RFC = 'SUPPLEMENTARY THEN REPEAT FAILED COURSE'
    RFC_PCO = 'REPEAT FAILED COURSE THEN PROCEED WITH CARRYOVER'
    RFC_RFC = 'REPEAT FAILED CARRYOVER THEN REPEAT FAILED COURSE'


class ResultType(models.TextChoices):
    PAP = 'PAP'
    PCO = 'PCO'
    RFC = 'RFC'
    FAW = 'FAW'
    SUP = 'SUP'
    MGD = 'MGD'
    SAW = 'SAW'
    SUP_RFC = 'SUP_RFC'
    RFC_PCO = 'RFC_PCO'
    RFC_RFC = 'RFC_RFC'


class CourseAttempt(models.TextChoices):
    NORMAL = 'NORMAL'
    CARRYOVER = 'CARRYOVER'
    REPEAT = 'REPEAT'  
    SUP = 'SUP'

      
class AppealStatus(models.TextChoices):
    PENDING = 'PENDING'
    GRADED = 'GRADED'
    RESOLVED = 'RESOLVED'


class SUPStatus(models.TextChoices):
    PENDING = 'PENDING'
    GRADED = 'GRADED'


class AppealType(models.TextChoices):
    COURSE_REMARK = 'COURSE REMARK'
    GRADE_CORRECTION = 'GRADE CORRECTION'


class AssessmentVersion(SarisModel):
    id = models.BigAutoField(primary_key=True, editable=False, unique=True)
    version = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Assessment Version'
        verbose_name_plural = 'assessment version'

    def __str__(self) -> str:
        return self.version
    
    @staticmethod
    def get_active():
        version = AssessmentVersion.objects.filter(is_active=True).first()
        if not version:
            raise AssessmentVersionNotFoundException
        return version
        
    @staticmethod
    def check_active():
        version = AssessmentVersion.objects.filter(is_active=True).first()
        if not version:
            raise AssessmentVersionNotFoundException
    
    @staticmethod
    def get_version(version):
        version = AssessmentVersion.objects.filter(version=version).first()
        if not version:
            raise AssessmentVersionNotFoundException
        return version


class GradeSchemeVersion(SarisModel):
    id = models.BigAutoField(primary_key=True, editable=False, unique=True)
    version = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Grade Scheme Version'
        verbose_name_plural = 'grade scheme version'

    def __str__(self) -> str:
        return self.version
    
    @staticmethod
    def get_active():
        version = GradeSchemeVersion.objects.filter(is_active=True).first()
        if not version:
            raise GradeSchemeVersionNotFoundException
        return version
    
    @staticmethod
    def get_version(version):
        version = GradeSchemeVersion.objects.filter(version=version).first()
        if not version:
            raise GradeSchemeVersionNotFoundException
        return version


class GradeScheme(SarisModel):
    id = models.BigAutoField(primary_key=True, editable=False, unique=True)
    min_grade = models.FloatField()
    max_grade = models.FloatField()
    letter_grade = models.CharField(max_length=255)
    grade_point = models.FloatField()
    grade_quality = models.CharField(max_length=255)
    decision = models.CharField(max_length=255)
    grade_scheme_version = models.ForeignKey(GradeSchemeVersion, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        verbose_name = 'Grade Scheme'
        verbose_name_plural = 'grade scheme'
        ordering = ['-min_grade']

    def __str__(self) -> str:
        return self.letter_grade


class AwardScheme(SarisModel):
    DEFAULT_CLASS = "PASS"
    id = models.BigAutoField(primary_key=True, editable=False, unique=True)
    program_type = models.CharField(max_length=255, choices=ProgramType.choices)
    min_cgpa = models.FloatField()
    max_cgpa = models.FloatField()
    repeated = models.BooleanField( default=False)
    award_class = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    assessment_version = models.ForeignKey(AssessmentVersion, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        verbose_name = 'Award Scheme'
        verbose_name_plural = 'award scheme'

    def __str__(self) -> str:
        return self.award_class


class AssessmentRule(SarisModel):
    id = models.BigAutoField(primary_key=True, editable=False, unique=True)
    program_type = models.CharField(max_length=255, choices=ProgramType.choices)
    min_cgpa = models.FloatField(verbose_name="Minimum GPA")
    max_cgpa = models.FloatField(verbose_name="Maximum GPA")
    is_first_year = models.BooleanField( default=False)
    is_repeating = models.BooleanField( default=False)
    has_failed_core = models.BooleanField( default=False)
    has_failed_sup= models.BooleanField( default=False)
    has_failed_cov = models.BooleanField( default=False)
    has_failed_rfc = models.BooleanField( default=False)
    decision = models.CharField(max_length=255, choices=ResultType.choices,default=None)
    assessment_version = models.ForeignKey(AssessmentVersion, on_delete=models.DO_NOTHING, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Assessment Rule'
        verbose_name_plural = 'assessment rule'

    def __str__(self) -> str:
        return f"{self.program_type}-{self.assessment_version}"


class CompensationRule(SarisModel):
    id = models.BigAutoField(primary_key=True, editable=False, unique=True)
    program_level = models.CharField(max_length=255, choices=ProgramLevel.choices)
    withdrawal_semester = models.IntegerField()
    previous_semester = models.IntegerField()
    previous_result = models.CharField(max_length=255, choices=ResultType.choices, default=ResultType.PAP)
    award = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Compensation Rule'
        verbose_name_plural = 'compensation rule'


class StudentCourse(SarisModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.DO_NOTHING)
    academic_semester = models.ForeignKey(AcademicSemester, on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    course_type = models.CharField(max_length=255, choices=CourseType.choices)
    course_attempt = models.CharField(max_length=255, choices=CourseAttempt.choices)
    semester = models.IntegerField()
    continous_grade = models.FloatField(blank=True, null=True)
    endsemester_grade = models.FloatField(blank=True, null=True)
    final_grade = models.FloatField(blank=True, null=True)
    grade_point = models.FloatField(blank=True, null=True)
    letter_grade = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        verbose_name = 'Student Course'
        verbose_name_plural = 'student courses'
        ordering = ['course__code']

    def __str__(self) -> str:
        return self.course.name
    
    def is_graded(self):
        if self.final_grade and self.grade_point and self.letter_grade:
            return True
        else:
            return False


class SemesterResult(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.DO_NOTHING)
    academic_semester = models.ForeignKey(AcademicSemester, on_delete=models.DO_NOTHING)
    semester = models.IntegerField()
    semester_gpa = models.FloatField(blank=True, null=True)
    semester_credits = models.FloatField(blank=True, null=True)
    cumulative_gpa = models.FloatField(blank=True, null=True)
    cumulative_credits = models.FloatField(blank=True, null=True)
    decision = models.CharField(max_length=255, choices=ResultType.choices,default=None)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Semester Result'
        verbose_name_plural = 'semester results'
        ordering = ['created_at']

    def __str__(self) -> str:
        return self.decision
    
    def is_first_semester(self) -> bool:
        return self.semester == 1

    def is_final_semester(self) -> bool:
        return self.semester == self.enrollment.program.semesters

    def is_pap(self) -> bool:
        return self.decision == ResultType.PAP

    def is_sup(self) -> bool:
        return self.decision == ResultType.SUP

    def is_pco(self) -> bool:
        return self.decision == ResultType.PCO

    def is_rfc(self) -> bool:
        return self.decision == ResultType.RFC

    def is_faw(self) -> bool:
        return self.decision == ResultType.FAW

    def is_sup_and_rfc(self) -> bool:
        return self.decision == ResultType.SUP_RFC


    def is_rfc_and_pco(self) -> bool:
        return self.decision == ResultType.RFC_PCO

    def is_rfc_and_rfc(self) -> bool:
        return self.decision == ResultType.RFC_RFC


class CourseAppeal(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.DO_NOTHING)
    academic_semester = models.ForeignKey(AcademicSemester, on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    course_type = models.CharField(max_length=255, choices=CourseType.choices)
    course_attempt = models.CharField(max_length=255, choices=CourseAttempt.choices)
    semester = models.IntegerField()
    appeal_type = models.CharField(max_length=255, choices=AppealType.choices)
    old_continous_grade = models.FloatField(blank=True, null=True)
    old_endsemester_grade = models.FloatField(blank=True, null=True)
    continous_grade = models.FloatField(blank=True, null=True)
    endsemester_grade = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=255, choices=AppealStatus.choices, default=AppealStatus.PENDING)
    
    class Meta:
        verbose_name = 'Course Appeal'
        verbose_name_plural = 'course appeals'
        ordering = ['-semester']

    def __str__(self) -> str:
        return f"{self.enrollment.student.student_number}-{self.course.name}"
    
    @property
    def student(self):
        return self.enrollment.student
    
    def is_graded(self):
        return self.status==AppealStatus.GRADED
    
    def is_resolved(self):
        return self.status==AppealStatus.RESOLVED
    

class Supplementary(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.DO_NOTHING)
    academic_semester = models.ForeignKey(AcademicSemester, on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    course_type = models.CharField(max_length=255, choices=CourseType.choices)
    course_attempt = models.CharField(max_length=255, choices=CourseAttempt.choices)
    semester = models.IntegerField()
    continous_grade = models.FloatField(blank=True, null=True)
    endsemester_grade = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=255, choices=SUPStatus.choices, default=SUPStatus.PENDING)
    
    class Meta:
        verbose_name = 'Supplementary'
        verbose_name_plural = 'supplementary'
        ordering = ['-semester']

    def __str__(self) -> str:
        return f"{self.enrollment.student.student_number}-{self.course.name}"
    
    @property
    def student(self):
        return self.enrollment.student
    

class LecturerCourse(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    lecturer = models.ForeignKey(Staff, on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = 'Lecturer Course'
        verbose_name_plural = 'lecturer courses'

    def __str__(self) -> str:
        return self.course.name


class GradeBenchMark(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    continous_grade = models.FloatField()
    endsemester_grade = models.FloatField()
    version = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Grade Bench Mark'
        verbose_name_plural = 'grade benchmark'
   
    def get_active():
        active = GradeBenchMark.objects.filter(is_active=True).first()
        if not active:
            raise GradeBenchMarkNotFoundException
        return active
    
    def get_by_version(version):
        benchmark = GradeBenchMark.objects.filter(version=version).first()
        if not benchmark:
            raise GradeBenchMarkNotFoundException
        return benchmark


class PassMark(SarisModel):
    id = models.BigAutoField(primary_key=True, editable=False, unique=True)
    program_type = models.CharField(max_length=255, choices=ProgramType.choices)
    pass_grade = models.FloatField()
    pass_cgpa = models.FloatField()
    
    class Meta:
        verbose_name = 'Grade Pass Mark'
        verbose_name_plural = 'grade passmark'

    def get_by_program_type(program_type):
        passmark = PassMark.objects.filter(program_type=program_type).first()
        if not passmark:
            raise PassMarkNotFoundException
        return passmark


class PublishedResult(SarisModel):
    id = models.UUIDField(primary_key=True, editable=False, unique=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.DO_NOTHING)
    academic_semester = models.ForeignKey(AcademicSemester, on_delete=models.DO_NOTHING)
    semester = models.IntegerField()
    semester_gpa = models.FloatField(blank=True, null=True)
    semester_credits = models.FloatField(blank=True, null=True)
    cumulative_gpa = models.FloatField(blank=True, null=True)
    cumulative_credits = models.FloatField(blank=True, null=True)
    decision = models.CharField(max_length=255, choices=ResultType.choices, default=None)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Published Results'
        verbose_name_plural = 'published results'

    def __str__(self) -> str:
        return f"{self.decision} - {self.description}"
    
    def is_first_semester(self):
        return self.semester == 1


class PublishedGrade(SarisModel):

    id = models.UUIDField(primary_key=True, editable=False, unique=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.DO_NOTHING)
    academic_semester = models.ForeignKey(AcademicSemester, on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    course_type = models.CharField(max_length=255, choices=CourseType.choices)
    course_attempt = models.CharField(max_length=255, choices=CourseAttempt.choices)
    semester = models.IntegerField()
    continous_grade = models.FloatField(blank=True, null=True)
    endsemester_grade = models.FloatField(blank=True, null=True)
    final_grade = models.FloatField(blank=True, null=True)
    grade_point = models.FloatField(blank=True, null=True)
    letter_grade = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        verbose_name = 'Published Grades'
        verbose_name_plural = 'published grades'
        ordering = ['course__code']

    def __str__(self) -> str:
        return self.course.name


class GradeBook(WorkMixin, SarisModel):
    FILE_UPLOAD = get_file_path("gradebook", APP_NAME)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.DO_NOTHING)
    academic_semester = models.ForeignKey(AcademicSemester, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=45, choices=WorkStatus.choices, default=WorkStatus.PENDING)
    error = models.CharField(max_length=255, blank=True, null=True)
    pdf_file = models.FileField(upload_to=FILE_UPLOAD, null=True, blank=True)

    class Meta:
        verbose_name = 'Grade Book'
        verbose_name_plural = 'grade books'

    def __str__(self):
        return f"{self.faculty.name} ({self.academic_semester.name})"
    