import django_filters
from django.db.models import Q
from saris_curriculum.models import Program, ProgramType
from saris_graduation.models import Booklet, Candidate, Session


class CandidateFilter(django_filters.FilterSet):
    student_number = django_filters.NumberFilter(field_name='enrollment__student__student_number', label='Student number')
    program_type = django_filters.ChoiceFilter(choices=ProgramType.choices, field_name='enrollment__program__program_type', label='Program type')
    program = django_filters.ModelChoiceFilter(queryset=Program.get_all(), field_name='enrollment__program', label='Program')
    
    class Meta:
        model = Candidate
        fields = ['student_number',  'program_type', 'program']

    @property
    def qs(self):
        parent = super().qs
        user = self.request.user.staff
        return parent.filter(enrollment__campus=user.campus)
    

class BookletFilter(django_filters.FilterSet):
    session = django_filters.ModelChoiceFilter(queryset=Session.get_all())

    class Meta:
        model = Booklet
        fields = ['session']



