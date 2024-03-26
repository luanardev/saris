from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from saris_institution.models import Department
from .models import Program, Course, MasterCurriculum


class ProgramResource(resources.ModelResource):
    id = fields.Field(attribute='id', readonly=True)
    code = fields.Field(attribute='code', column_name='PROGRAM_CODE')
    name = fields.Field(attribute='name', column_name='PROGRAM_NAME')
    field_name = fields.Field(attribute='field_name', column_name='FIELD_NAME')
    version = fields.Field(attribute='version', column_name='PROGRAM_VERSION')
    years = fields.Field(attribute='years', column_name='PROGRAM_YEARS')
    semesters = fields.Field(attribute='semesters', column_name='PROGRAM_SEMESTERS')
    program_level = fields.Field(attribute='program_level', column_name='PROGRAM_LEVEL')
    program_type = fields.Field(attribute='program_type', column_name='PROGRAM_TYPE')
    department = fields.Field(attribute='department', column_name='DEPARTMENT_CODE', widget=ForeignKeyWidget(Department, field='code'))

    class Meta:
        model = Program
        import_id_fields = ['code']
        fields = ['id','code', 'name', 'field_name', 'version', 'years', 'semesters', 'program_level', 'program_type', 'department']


class CourseResource(resources.ModelResource):
    id = fields.Field(attribute='id', readonly=True)
    code = fields.Field(attribute='code', column_name='COURSE_CODE')
    name = fields.Field(attribute='name', column_name='COURSE_NAME')
    version = fields.Field(attribute='version', column_name='COURSE_VERSION')
    credit_hours = fields.Field(attribute='credit_hours', column_name='CREDIT_HOURS')
    department = fields.Field(attribute='department', column_name='DEPARTMENT_CODE', widget=ForeignKeyWidget(Department, field='code'))

    class Meta:
        model = Course
        import_id_fields = ['code']
        fields = ['id', 'code', 'name', 'version','credit_hours', 'department',]


class MasterCurriculumResource(resources.ModelResource):
    id = fields.Field(attribute='id', readonly=True)
    semester = fields.Field(attribute='semester', column_name='SEMESTER')
    version = fields.Field(attribute='version', column_name='VERSION')
    program = fields.Field(attribute='program', column_name='PROGRAM_CODE', widget=ForeignKeyWidget(Program, field='code'))
    course = fields.Field(attribute='course', column_name='COURSE_CODE', widget=ForeignKeyWidget(Course, field='code'))
    course_type = fields.Field(attribute='course_type', column_name='COURSE_TYPE')

    class Meta:
        model = MasterCurriculum
        import_id_fields = ['program', 'course', 'version']
        fields = ['id', 'program', 'course', 'course_type', 'semester', 'version',]
    
