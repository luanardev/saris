import django_filters
from django.db.models import Q
from .models import Student


class StudentFilter(django_filters.FilterSet):
    student_number = django_filters.CharFilter(field_name="student_number", label="Student number")
    
    class Meta:
        model = Student
        fields = ['student_number']


class StudentSearch(django_filters.FilterSet):
    query = django_filters.CharFilter(method='search', label="Search")

    class Meta:
        model = Student
        fields = ['query']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(student_number__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email_address__icontains=value)
        )
