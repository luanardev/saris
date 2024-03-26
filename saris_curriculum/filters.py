import django_filters

from saris_institution.models import Department
from .models import ConfiguredCourse, ConfiguredCurriculum, Course, Program, MasterCurriculum, StatusType

def get_user_department(request):
    department = request.user.staff.department
    return Department.filter(pk=department.pk)


def get_courses_by_department(request):
    department = request.user.staff.department
    return Course.filter(department=department, status=StatusType.ACTIVE)


def get_programs_by_department(request):
    department = request.user.staff.department
    return Program.filter(department=department, status=StatusType.ACTIVE)


def get_programs_by_campus(request):
    campus = request.user.staff.campus
    return Program.filter(department__faculty__campus=campus, status=StatusType.ACTIVE)


class ProgramFilter(django_filters.FilterSet):
    department = django_filters.ModelChoiceFilter(queryset=get_user_department)
    class Meta:
        model = Program
        fields = ['code', 'name', 'version', 'department', 'status']

class CourseFilter(django_filters.FilterSet):
    department = django_filters.ModelChoiceFilter(queryset=get_user_department)
    class Meta:
        model = Course
        fields = ['code', 'name', 'version', 'department', 'status']

class MasterCurriculumFilter(django_filters.FilterSet):
    course_code = django_filters.CharFilter(field_name='course__code', label='Course code')
    class Meta:
        model = MasterCurriculum
        fields = ['course_code',  'course_type', 'semester']

class ConfiguredCurriculumFilter(django_filters.FilterSet):
    program = django_filters.ModelChoiceFilter(queryset=get_programs_by_department)
    class Meta:
        model = ConfiguredCurriculum
        fields = ['program', 'academic_semester',  'semester', 'version']

class ConfiguredCourseFilter(django_filters.FilterSet):
    course_code = django_filters.CharFilter(field_name='course__code', label='Course code')
    class Meta:
        model = ConfiguredCourse
        fields = ['course_code',  'course_type', 'semester']
