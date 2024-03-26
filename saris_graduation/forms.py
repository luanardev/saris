from django import forms
from saris_graduation.models import Session


class SessionForm(forms.ModelForm):

    class Meta:
        model = Session 
        fields = ['name', 'academic_year', 'graduation_date']
        widgets = {'graduation_date': forms.DateInput(attrs={'type': 'date'})}


class GraduationForm(forms.Form):
    session = forms.ModelChoiceField(required=True, queryset=Session.get_all(), label="Graduation session")

    class Meta:
        fields = ["session"]