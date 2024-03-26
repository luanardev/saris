import django_filters
from django.db.models import Q
from saris_calendar.filters import get_academic_semester_by_campus
from saris_curriculum.models import ProgramType
from saris_institution.filters import get_campuses_by_user
from .models import Enrollment, EnrollmentStatus, Withdrawal


class EnrollmentFilter(django_filters.FilterSet):
    student_number = django_filters.NumberFilter(field_name='student__student_number', label='Student number')
    program_type = django_filters.ChoiceFilter(choices=ProgramType.choices, field_name='program__program_type', label='Program type')
    date_range = django_filters.DateRangeFilter(field_name='created_at', label='Admission date')
    class Meta:
        model = Enrollment
        fields = ['student_number', 'program', 'academic_year', 'program_type', 'intake_type', 'semester', 'date_range', 'status']

    @property
    def qs(self):
        parent = super().qs
        user = self.request.user.staff
        return parent.filter(campus=user.campus)
    
    
class EnrollmentSearch(django_filters.FilterSet):
    query = django_filters.CharFilter(method='search', label="Search")

    class Meta:
        model = Enrollment
        fields = ['query']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(status=EnrollmentStatus.ENROLLED) &
            Q(serial_number__icontains=value) |
            Q(student__student_number__icontains=value) |
            Q(student__first_name__icontains=value) |
            Q(student__last_name__icontains=value) 
        )


class WithdrawalFilter(django_filters.FilterSet):
    student_number = django_filters.NumberFilter(field_name='enrollment__student__student_number', label='Student number')
    academic_semester = django_filters.ModelChoiceFilter(queryset=get_academic_semester_by_campus)

    class Meta:
        model = Withdrawal
        fields = ['student_number', 'academic_semester', 'withdrawal_type']


class AdmissionLettersFilter(django_filters.FilterSet):
    date_range = django_filters.DateRangeFilter(field_name='created_at', label='Admission date')
    campus = django_filters.ModelChoiceFilter(queryset=get_campuses_by_user)
    
    class Meta:
        model = Enrollment
        fields = ['academic_year', 'campus', 'program', 'intake_type', 'date_range']

