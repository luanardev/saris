import uuid
from django.db import models
from django_countries.fields import CountryField
from saris.models import SarisModel
from saris.utils import get_file_path
from saris_institution.apps import SarisInstitutionConfig

APP_NAME = SarisInstitutionConfig.name


class University(SarisModel):
    LOGO_UPLOAD = get_file_path("logo", APP_NAME)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    acronym = models.CharField(max_length=255, blank=True, null=True)
    postal_address = models.CharField(max_length=255, blank=True, null=True)
    physical_address = models.CharField(max_length=255, blank=True, null=True)
    email_address = models.EmailField(max_length=255, blank=True, null=True)
    telephone_one = models.CharField(max_length=100, blank=True, null=True)
    telephone_two = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to=LOGO_UPLOAD, max_length=255, blank=True, null=True)
    favicon = models.ImageField(upload_to=LOGO_UPLOAD, max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255,  null=True, choices=CountryField().choices + [('', 'Select Country')])
    website_domain = models.CharField(max_length=255, blank=True, null=True)
    email_domain = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'University'
        verbose_name_plural = 'university'

    def __str__(self):
        return self.name
    
    @staticmethod
    def get_info():
        return University.objects.first()


class Campus(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    postal_address = models.CharField(max_length=255, blank=True, null=True)
    email_address = models.EmailField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Campus'
        verbose_name_plural = 'campuses'

    def __str__(self):
        return self.name


class Faculty(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = 'Faculty'
        verbose_name_plural = 'faculties'
    def __str__(self):
        return self.name


class Department(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    faculty = models.ForeignKey(Faculty, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'departments'

    def __str__(self):
        return self.name


class Venue(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    class_capacity = models.IntegerField(blank=True, null=True)
    exam_capacity = models.IntegerField(blank=True, null=True)
    campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = 'Venue'
        verbose_name_plural = 'venues'
    def __str__(self):
        return f"{self.campus.code}-{self.name}"


