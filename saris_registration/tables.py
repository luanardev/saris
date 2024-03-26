import django_tables2 as tables
from saris.tables import SelectAllCheckBoxColumn
from saris_assessment.models import StudentCourse
from saris_registration.models import Registration


class RegistrationTable(tables.Table):
    student_number = tables.Column(
        verbose_name="ID",
        accessor="enrollment__student__student_number",
        linkify=("registration:details", [tables.A("pk")])
    )
    
    student = tables.Column(
        verbose_name="STUDENT",
        accessor="enrollment__student",
        linkify=("registration:details", [tables.A("pk")])
    )
    
    program = tables.Column(
        verbose_name="PROGRAM",
        accessor="enrollment__program",
    )
    
    academic_semester = tables.Column(
        verbose_name="ACADEMIC SEMESTER",
        accessor="academic_semester",
    )
    
    semester = tables.Column(
        verbose_name="SEMESTER",
        accessor="semester",
    )
    
    type = tables.Column(
        verbose_name="TYPE",
        accessor="type",
    )
    
    class Meta:
        model = Registration
        fields = ['student_number', 'student',  'program', 'academic_semester', 'semester','type',]


class StudentCourseTable(tables.Table):
    selection = SelectAllCheckBoxColumn(accessor="pk", orderable=False)

    course_code = tables.Column(
        verbose_name="COURSE CODE",
        accessor="course__code",
    )

    course_name = tables.Column(
        verbose_name="COURSE NAME",
        accessor="course__name",
    )

    credit_hours = tables.Column(
        verbose_name="CREDIT HOURS",
        accessor="course__credit_hours",
    )

    course_type = tables.Column(
        verbose_name="COURSE TYPE",
        accessor="course_type",
    )

    course_attempt = tables.Column(
        verbose_name="COURSE ATTEMPT",
        accessor="course_attempt",
    )

    cas_grade = tables.Column(
        verbose_name="CAS GRADE",
        accessor="continous_grade",
    )

    eos_grade = tables.Column(
        verbose_name="EOS GRADE",
        accessor="endsemester_grade",
    )

    final_grade = tables.Column(
        verbose_name="FINAL GRADE",
        accessor="final_grade",
    )

    class Meta:
        model = StudentCourse
        fields = ['selection', 'course_code', 'course_name', 'course_type',
                  'course_attempt', 'credit_hours', 'cas_grade', 'eos_grade', 'final_grade']
