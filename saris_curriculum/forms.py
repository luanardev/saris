from django import forms
from django.core.validators import FileExtensionValidator
from .models import (
    Program, Course,
    ConfiguredCourse, 
    ConfiguredCurriculum, 
    MasterCurriculum
)


class ImportForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}),
        required=True,
        label="Excel File",
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        help_text="Upload Excel sheet"
    )
    

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        exclude = ['max_semesters', 'summary']
        

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'version', 'credit_hours', 'department', 'status',]


class MasterCurriculumForm(forms.ModelForm):
    class Meta:
        model = MasterCurriculum
        fields = ['course', 'course_type', 'semester', 'version', ]
        exclude = ['program']


class CurriculumConfigurationForm(forms.ModelForm):
    class Meta:
        model = ConfiguredCurriculum
        fields = ['program', 'academic_semester', 'semester', ]


class CourseConfigurationForm(forms.ModelForm):
    class Meta:
        model = ConfiguredCourse
        fields = ['course', 'course_type', 'semester', ]
        exclude = ['curriculum']
