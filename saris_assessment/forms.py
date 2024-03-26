from django import forms
from saris_calendar.filters import get_academic_semester_by_campus
from saris_institution.filters import get_campuses_by_user, get_faculties_by_campus


class GradeProcessingForm(forms.Form):
    academic_semester = forms.ModelChoiceField(required=True, queryset=None)
    
    class Meta:
        fields = ["academic_semester",]
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields["academic_semester"].queryset = get_academic_semester_by_campus(request)


class CampusGradeProcessingForm(forms.Form):
    campus = forms.ModelChoiceField(required=True, queryset=None)
    
    class Meta:
        fields = ["campus",]
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields["campus"].queryset = get_campuses_by_user(request)


class GradeBookForm(forms.Form):
    faculty = forms.ModelChoiceField(required=True, queryset=None)
    academic_semester = forms.ModelChoiceField(required=True, queryset=None)

    
    class Meta:
        fields = ["academic_semester", "faculty"]
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields["academic_semester"].queryset = get_academic_semester_by_campus(request)
        self.fields["faculty"].queryset = get_faculties_by_campus(request)