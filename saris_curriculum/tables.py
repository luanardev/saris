import django_tables2 as tables
from .models import ConfiguredCourse, ConfiguredCurriculum, Program, Course, MasterCurriculum


class ProgramTable(tables.Table):
  
    code = tables.Column(
        verbose_name="CODE",
        accessor="code",
        linkify=("curriculum:program.details", [tables.A("pk")])
    )
    
    name = tables.Column(
        verbose_name="NAME",
        accessor="name",
        linkify=("curriculum:program.details", [tables.A("pk")])
    )
    
    version = tables.Column(
        verbose_name="VERSION",
        accessor="version",
    )
    
    years = tables.Column(
        verbose_name="YEARS",
        accessor="years",
    )
    
    program_level = tables.Column(
        verbose_name="LEVEL",
        accessor="program_level",
    )
    
    program_type = tables.Column(
        verbose_name="TYPE",
        accessor="program_type",
    )
    
    department = tables.Column(
        verbose_name="DEPT",
        accessor="department",
    )
    
    status = tables.Column(
        verbose_name="STATUS",
        accessor="status",
    )
    
    class Meta:
        model = Program
        fields = ['code', 'name', 'version', 'years', 'program_level', 'program_type', 'department', 'status',]


class CourseTable(tables.Table):
    
    code = tables.Column(
        verbose_name="CODE",
        accessor="code",
        linkify=("curriculum:course.details", [tables.A("pk")])
    )

    name = tables.Column(
        verbose_name="NAME",
        accessor="name",
        linkify=("curriculum:course.details", [tables.A("pk")])
    )

    version = tables.Column(
        verbose_name="VERSION",
        accessor="version",
    )
    
    credit_hours = tables.Column(
        verbose_name="CREDIT HOURS",
        accessor="credit_hours",
    )
    
    department = tables.Column(
        verbose_name="DEPT",
        accessor="department",
    )
    
    status = tables.Column(
        verbose_name="STATUS",
        accessor="status",
    )
    
    class Meta:
        model = Course
        fields = ['code', 'name', 'version', 'credit_hours', 'department', 'status',]
        

class MasterCurriculumTable(tables.Table):
    course_code = tables.Column(
        verbose_name="CODE",
        accessor="course__code",
        linkify=("curriculum:curriculum.update", [tables.A("pk")])
    )

    course_name = tables.Column(
        verbose_name="COURSE",
        accessor="course__name",
        linkify=("curriculum:curriculum.update", [tables.A("pk")])
    )
    
    version = tables.Column(
        verbose_name="VERSION",
        accessor="version",
    )
    
    course_type = tables.Column(
        verbose_name="TYPE",
        accessor="course_type",
    )
    
    semester = tables.Column(
        verbose_name="SEMESTER",
        accessor="semester",
    )
    
    class Meta:
        model = MasterCurriculum
        fields = ['course_code', 'course_name', 'version', 'course_type', 'semester',]


class ConfiguredCurriculumTable(tables.Table):
    program_code = tables.LinkColumn(viewname="curriculum:configuration.details", text=lambda record: record.program.code, args=[tables.A("pk")])
    program_name = tables.LinkColumn(viewname="curriculum:configuration.details", text=lambda record: record.program.name, args=[tables.A("pk")])
    
    program_code = tables.Column(
        verbose_name="CODE",
        accessor="program__code",
        linkify=("curriculum:configuration.details", [tables.A("pk")])
    )

    program_name = tables.Column(
        verbose_name="PROGRAM",
        accessor="program__name",
        linkify=("curriculum:configuration.details", [tables.A("pk")])
    )
    
    academic_semester = tables.Column(
        verbose_name="ACADEMIC SEMESTER",
        accessor="academic_semester",
    )
    
    semester = tables.Column(
        verbose_name="SEMESTER",
        accessor="semester",
    )
    
    version = tables.Column(
        verbose_name="VERSION",
        accessor="version",
    )
    
    class Meta:
        model = ConfiguredCurriculum
        fields = ['program_code', 'program_name', 'academic_semester', 'semester', 'version']


class ConfiguredCourseTable(tables.Table):
    action = tables.LinkColumn(viewname="curriculum:configuration.deletecourse", text="delete", args=[tables.A("pk")])
    
    course_code = tables.Column(
        verbose_name="CODE",
        accessor="course__code",
    )

    course_name = tables.Column(
        verbose_name="COURSE",
        accessor="course__name",
    )

    course_type = tables.Column(
        verbose_name="TYPE",
        accessor="course_type",
    )

    semester = tables.Column(
        verbose_name="SEMESTER",
        accessor="semester",
    )
    class Meta:
        model = ConfiguredCourse
        fields = ['course_code', 'course_name', 'course_type', 'semester', 'action']
