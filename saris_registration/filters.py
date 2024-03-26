import django_filters
from saris_curriculum.models import Program, ProgramType, StatusType
from saris_calendar.filters import get_academic_semester_by_campus
from .models import Registration

class RegistrationFilter(django_filters.FilterSet):
    student_number = django_filters.CharFilter(field_name='enrollment__student__student_number', label='Student number')
    program = django_filters.ModelChoiceFilter(queryset=Program.filter(status=StatusType.ACTIVE), field_name='enrollment__program', label='Program')
    academic_semester = django_filters.ModelChoiceFilter(queryset=get_academic_semester_by_campus, field_name='academic_semester', label='Academic Semester')
    
    class Meta:
        model = Registration
        fields = ['student_number', 'program', 'academic_semester', 'semester']