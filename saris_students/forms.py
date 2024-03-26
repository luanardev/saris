from django import forms
from .models import Kinsman, Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['student_number', 'saris_email', 'saris_username', 'saris_password', 'passcode', 'profile_picture', 'passport_photo', 'signature', 'qrcode_url']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'})}


class IDCardForm(forms.ModelForm):
    passport_photo = forms.ImageField(required=True, label="Passport Size Photo")
    signature = forms.ImageField(required=True, label="Student Signature")
    class Meta:
        model = Student
        fields = ['passport_photo', 'signature',]


class KinsmanForm(forms.ModelForm):
    class Meta:
        model = Kinsman
        exclude = ['student']

    