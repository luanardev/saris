import django_tables2 as tables

from saris.tables import SelectAllCheckBoxColumn
from .models import CourseAppeal, GradeBook, Supplementary


class GradeBookTable(tables.Table):
    selection = SelectAllCheckBoxColumn(accessor="pk", orderable=False)
   
    faculty = tables.Column(
        verbose_name="FACULTY",
        accessor="faculty",
        linkify=("assessment:gradebook.download", [tables.A("pk")] )
    )
     
    academic_semester = tables.Column(
        verbose_name="ACADEMIC SEMESTER",
        accessor="academic_semester",
        linkify=("assessment:gradebook.download", [tables.A("pk")] )
    )
    
    status = tables.Column(
        verbose_name="STATUS",
        accessor="status",
    )
    
    created_at = tables.Column(
        verbose_name="GENERATED ON",
        accessor="created_at",
    )

    class Meta:
        model = GradeBook
        fields = ['selection','faculty', 'academic_semester', 'status', 'created_at']
        

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

    appeal_type = tables.Column(
        verbose_name="APPEAL",
        accessor="appeal_type",
    )

    status = tables.Column(
        verbose_name="STATUS",
        accessor="status",
    )

    action = tables.LinkColumn(
        viewname="assessment:appeals.details",
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
            'academic_semester', 'semester', 'appeal_type', 'status', 'action'
        ]


class SupplementaryTable(tables.Table):

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
        viewname="assessment:supplementary.details",
        text="View",
        verbose_name="ACTION",
        args=[tables.A("pk")],
        attrs={
            "a": {"class": "btn btn-sm btn-primary"}
        }
    )

    class Meta:
        model = Supplementary
        fields = [
            'student_number', 'student_name', 'program_code',  'course_name', 
            'academic_semester', 'semester', 'status', 'action'
        ]
