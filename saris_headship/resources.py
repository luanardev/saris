from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from account.models import User
from saris_curriculum.models import Course
from saris_assessment.models import LecturerCourse


class LecturerCourseResource(resources.ModelResource):
    id = fields.Field(attribute='id', readonly=True)
    course = fields.Field(attribute='course', column_name='COURSE_CODE', widget=ForeignKeyWidget(Course, field='code'))
    lecturer = fields.Field(attribute='lecturer', column_name='LECTURER_EMAIL', widget=ForeignKeyWidget(User, field='email'))

    class Meta:
        model = LecturerCourse
        import_id_fields = ['course', 'lecturer']
        fields = ['id', 'course', 'lecturer',]
