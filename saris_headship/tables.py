import django_tables2 as tables
from saris.tables import SelectAllCheckBoxColumn
from saris_assessment.models import CourseAppeal, LecturerCourse


class CourseAllocationTable(tables.Table):
    selection = SelectAllCheckBoxColumn(accessor="pk", orderable=False)
    
    course_code = tables.Column(
        verbose_name="COURSE CODE",
        accessor="course__code",
    )

    course_name = tables.Column(
        verbose_name="COURSE NAME",
        accessor="course__name",
    )
    
    lecturer = tables.Column(
        verbose_name="LECTURER NAME",
        accessor="lecturer__name",
    )
    
    email = tables.EmailColumn(
        verbose_name="LECTURER EMAIL",
        accessor="lecturer__email",
    )
    
    class Meta:
        model = LecturerCourse
        fields = ['selection', 'course_code', 'course_name', 'lecturer', 'email']


class CourseAppealTable(tables.Table):

    student_number = tables.Column(
        verbose_name="ID",
        accessor="enrollment__student__student_number",
    )

    student_name = tables.Column(
        verbose_name="STUDENT",
        accessor="enrollment__student",
    )

    program_code = tables.Column(
        verbose_name="PROGRAM",
        accessor="enrollment__program__code",
    )

    course_name = tables.Column(
        verbose_name="COURSE",
        accessor="course__name",
    ) 

    academic_semester = tables.Column(
        verbose_name="ACADEMIC SEMESTER",
        accessor="academic_semester",
    )

    semester = tables.Column(
        verbose_name="SEMESTER",
        accessor="semester",
    )

    status = tables.Column(
        verbose_name="STATUS",
        accessor="status",
    )

    action = tables.LinkColumn(
        viewname="headship:courseappeal.details",
        text="View",
        verbose_name="ACTION",
        args=[tables.A("pk")],
        attrs={
            "a": {"class": "btn btn-sm btn-primary"}
        }
    )

    class Meta:
        model = CourseAppeal
        fields = [
            'student_number', 'student_name', 'program_code',  'course_name', 
            'academic_semester', 'semester', 'status', 'action'
        ]
