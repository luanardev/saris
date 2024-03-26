from django import forms

from saris_curriculum.models import Program
from saris_institution.models import Campus
from .models import Transfer


class ChangeProgramForm(forms.Form):
    student_number = forms.IntegerField(required=True, label="Student number")
    program = forms.ModelChoiceField(queryset=Program.get_all() ,required=True, label="Program requested")

    class Meta:
        model = Transfer
        fields = ['student_number', 'program']


class ChangeCampusForm(forms.Form):
    student_number = forms.IntegerField(required=True, label="Student number")
    campus = forms.ModelChoiceField(queryset=Campus.get_all() ,required=True, label="Campus requested")

    class Meta:
        model = Transfer
        fields = ['student_number', 'campus']