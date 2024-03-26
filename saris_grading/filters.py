import django_filters
from saris_assessment.models import StudentCourse
from saris_curriculum.filters import get_programs_by_campus

class ClassListFilter(django_filters.FilterSet):
    student_number = django_filters.NumberFilter(
        field_name="enrollment__student__student_number", 
        label="Student number")
    
    program = django_filters.ModelChoiceFilter(
        queryset=get_programs_by_campus,
        field_name="enrollment__program",
        label="Program")

    class Meta:
        model = StudentCourse
        fields = ['student_number', 'program']

    