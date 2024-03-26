from django import forms
from betterforms import multiform
from django.core.validators import FileExtensionValidator
from saris_students.models import Student
from .models import Enrollment, WithdrawalType


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = [
            'user', 'student_number', 'saris_email', 'saris_username', 'saris_password', 'passcode', 
            'profile_picture', 'passport_photo', 'signature', 'qrcode_url'
        ]
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'})}
        

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        exclude = [
            'student', 'serial_number', 'status', 
            'award_name', 'award_class', 'award_level', 'award_gpa',
            'is_compensated', 'is_graduating', 'is_certified', 'semester'
        ]


class EnrollmentUpdateForm(multiform.MultiModelForm):
    form_classes = {
        'student': StudentForm,
        'enrollment': EnrollmentForm,
    }


class WithdrawalForm(forms.Form):
    student_number = forms.IntegerField(required=True)
    withdrawal_type = forms.ModelChoiceField(queryset=WithdrawalType.get_all(), required=True)
    class Meta:
        fields = ['student_number', 'withdrawal_type',]


class ImportForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}),
        required=True,
        label="Excel File",
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        help_text="Upload Excel sheet"
    )
    
