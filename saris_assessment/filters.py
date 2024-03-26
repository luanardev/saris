import django_filters
from saris_calendar.filters import get_academic_semester_by_campus
from saris_institution.filters import get_faculties_by_campus
from .models import AppealStatus, AppealType, CourseAppeal, GradeBook, Supplementary


class GradeBookFilter(django_filters.FilterSet):
    faculty = django_filters.ModelChoiceFilter(queryset=get_faculties_by_campus)
    academic_semester = django_filters.ModelChoiceFilter(queryset=get_academic_semester_by_campus)
    
    class Meta:
        model = GradeBook
        fields = ['faculty', 'academic_semester']


class CourseAppealFilter(django_filters.FilterSet):
    student_number = django_filters.NumberFilter(field_name='enrollment__student__student_number', label='Student number')
    academic_semester = django_filters.ModelChoiceFilter(queryset=get_academic_semester_by_campus)
    appeal_type = django_filters.ChoiceFilter(choices=AppealType.choices)
    status = django_filters.ChoiceFilter(choices=AppealStatus.choices)

    class Meta:
        model = CourseAppeal
        fields = ['student_number', 'academic_semester', 'appeal_type', 'status']


class SupplementaryFilter(django_filters.FilterSet):
    student_number = django_filters.NumberFilter(field_name='enrollment__student__student_number', label='Student number')
    academic_semester = django_filters.ModelChoiceFilter(queryset=get_academic_semester_by_campus)
    status = django_filters.ChoiceFilter(choices=AppealStatus.choices)

    class Meta:
        model = Supplementary
        fields = ['student_number', 'academic_semester', 'status']