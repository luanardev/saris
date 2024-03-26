import django_filters
from account.filters import get_users_by_department
from saris_calendar.filters import get_academic_semester_by_campus
from saris_curriculum.filters import get_courses_by_department
from saris_assessment.models import AppealStatus, CourseAppeal, LecturerCourse


class CourseAllocationFilter(django_filters.FilterSet):
    course = django_filters.ModelChoiceFilter(queryset=get_courses_by_department)
    lecturer = django_filters.ModelChoiceFilter(queryset=get_users_by_department)

    class Meta:
        model = LecturerCourse
        fields = ['course', 'lecturer']


class CourseAppealFilter(django_filters.FilterSet):
    student_number = django_filters.NumberFilter(field_name='enrollment__student__student_number', label='Student number')
    academic_semester = django_filters.ModelChoiceFilter(queryset=get_academic_semester_by_campus)
    status = django_filters.ChoiceFilter(choices=AppealStatus.choices)

    class Meta:
        model = CourseAppeal
        fields = ['student_number', 'academic_semester', 'status']
