import django_filters
from django.db.models import Q
from saris_calendar.filters import get_academic_semester_by_campus
from .models import Invoice


class InvoiceFilter(django_filters.FilterSet):
    student_number = django_filters.NumberFilter(
        field_name='enrollment__student__student_number', label='Student number')
    date_range = django_filters.DateRangeFilter(
        field_name='invoice_date', label='Invoice date')   
    academic_semester = django_filters.ModelChoiceFilter(
        queryset=get_academic_semester_by_campus, field_name='academic_semester', label='Academic Semester')
    
    class Meta:
        model = Invoice
        fields = ['student_number', 'invoice_number', 'service', 'academic_semester', 'date_range', 'status']

    @property
    def qs(self):
        parent = super().qs
        user = self.request.user.staff
        return parent.filter(enrollment__campus=user.campus)


class InvoiceSearch(django_filters.FilterSet):
    query = django_filters.CharFilter(method='search', label="Search")

    class Meta:
        model = Invoice
        fields = ['query']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(enrollment__student__student_number__icontains=value) |
            Q(invoice_number__icontains=value) 
        )


