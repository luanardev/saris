import django_filters
from saris_calendar.filters import get_academic_semester_by_campus
from .models import Transfer


class TransferFilter(django_filters.FilterSet):
    student_number = django_filters.NumberFilter(field_name='enrollment__student__student_number', label='Student number')
    academic_semester = django_filters.ModelChoiceFilter(queryset=get_academic_semester_by_campus)

    class Meta:
        model = Transfer
        fields = ['student_number', 'academic_semester', 'transfer_type', 'request_status']