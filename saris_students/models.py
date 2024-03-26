import uuid
from django.conf import settings
from django.db import models
from django_countries.fields import CountryField
from saris.utils import current_year, random_string
from saris.models import SarisModel
from saris.choices import (TITLE_LIST, GENDER_LIST, MARITAL_LIST, RELATION_LIST)
from saris_students.apps import SarisStudentsConfig
from .exceptions import StudentNotFoundException

APP_NAME = SarisStudentsConfig.name

class Student(SarisModel):
    STUDENT_NUMBER_LENGTH = 6
    PASSCODE_LENGTH = 8

    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    student_number = models.IntegerField(blank=True, null=True, editable=False, unique=True)
    title = models.CharField(max_length=255, choices=TITLE_LIST)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, choices=GENDER_LIST)
    date_of_birth = models.DateField(blank=True, null=True)
    marital_status = models.CharField(max_length=255, choices=MARITAL_LIST, blank=True, null=True)
    email_address = models.EmailField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    postal_address = models.CharField(max_length=255, blank=True, null=True)
    physical_address = models.CharField(max_length=255, blank=True, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255,  null=True, choices=CountryField().choices + [('', 'Select Country')])
    passcode = models.CharField(max_length=20, blank=True, null=True)
   
   
    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'students'

    def set_user(self, user):
        self.user=user    

    def set_student_number(self):
        year = current_year()
        students_created_this_year = Student.objects.filter(created_at__year=year)
        count = students_created_this_year.count()
        if count == 0:
            two_digits_year = year % 100
            increment = 1
            padded_increment = str(increment).rjust(self.STUDENT_NUMBER_LENGTH, '0')
            student_number = f"{two_digits_year}{padded_increment}"
            self.student_number = student_number
        else:
            result = students_created_this_year.aggregate(max_field=models.Max("student_number"))
            increment = result["max_field"] + 1
            self.student_number = increment
    
    def set_default_passcode(self):
        passcode = random_string(self.PASSCODE_LENGTH)
        self.passcode = passcode

    @property
    def name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        else:
            return f"{self.first_name} {self.last_name}"

    @property
    def kinsman(self):
        from .models import Kinsman
        return Kinsman.objects.get(student_id=self.pk)
    
    @property
    def enrollment(self):
        from saris_admission.models import Enrollment
        return Enrollment.get_active(self.student_number)
    
    @property
    def campus(self):
        return self.enrollment.campus
    
    @property
    def profile_picture(self):
        return self.user.profile_picture
    
    @property
    def passport_photo(self):
        return self.user.passport_photo
    
    @property
    def signature(self):
        return self.user.signature
    
    def __str__(self):
        return self.name
    
    @staticmethod
    def get_by_student_number(student_number):
        student = Student.objects.filter(student_number=student_number).first()
        if not student:
            raise StudentNotFoundException
        return student
            

class Kinsman(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, choices=TITLE_LIST)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    relationship = models.CharField(max_length=255, choices=RELATION_LIST)
    occupation = models.CharField(max_length=255, blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True, null=True)
    email_address = models.CharField(max_length=255)
    postal_address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Kinsman'
        verbose_name_plural = 'kinsman'