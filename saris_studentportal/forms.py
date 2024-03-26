from django import forms
from saris_curriculum.models import Program
from saris_institution.models import Campus
from saris_studentportal.services import ResultsAccess
from saris_transfer.models import Transfer


class ChangeProgramForm(forms.Form):
    program = forms.ModelChoiceField(
        queryset=Program.get_all(), 
        required=True, 
        label="Program requested"
    )

    class Meta:
        model = Transfer
        fields = ['program']


class ChangeCampusForm(forms.Form):
    campus = forms.ModelChoiceField(
        queryset=Campus.get_all(),
        required=True, 
        label="Campus requested"
    )

    class Meta:
        model = Transfer
        fields = ['campus']


class CourseAppealForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=None, 
        required=True, 
        label="Courses", 
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        fields = ['course']

    def __init__(self, student_number, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = self.get_published_grades(student_number)

    def get_published_grades(self, student_number):
        result_access = ResultsAccess(student_number)
        grades = result_access.get_grades_without_appeal()
        return grades
