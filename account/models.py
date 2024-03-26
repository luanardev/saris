import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from saris_institution.models import Campus, Faculty, Department
from saris.utils import get_file_path
from account.apps import AccountConfig

APP_NAME = AccountConfig.name


class User(AbstractUser):
    SIGNATURE_UPLOAD = get_file_path("signature", APP_NAME)
    PROFILE_PICTURE_UPLOAD = get_file_path("profile_picture", APP_NAME)
    PASSPORT_PHOTO_UPLOAD = get_file_path("passport_photo", APP_NAME)
       
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True)
    is_student = models.BooleanField(_("student status"), default=False)
    profile_picture = models.ImageField(upload_to=PROFILE_PICTURE_UPLOAD, max_length=255, blank=True, null=True)
    passport_photo = models.ImageField(upload_to=PASSPORT_PHOTO_UPLOAD, max_length=255, blank=True, null=True)
    signature= models.ImageField(upload_to=SIGNATURE_UPLOAD, max_length=255, blank=True, null=True)

    def __str__(self):
        return self.get_full_name()
    
    def set_student(self):
        self.is_student = True

    def set_staff(self):
        self.is_staff = True

    def set_superuser(self):
        self.is_superuser = True
    
    def set_active(self):
        self.is_active = True

    def set_not_active(self):
        self.is_active = False

    def set_username(self, username):
        self.username = username

    def set_email(self, email):
        self.email = email

    def set_default_password(self):
        self.set_password("password")


class Staff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, blank=True, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.DO_NOTHING, blank=True, null=True)
    campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        verbose_name = 'Staff'
        verbose_name_plural = 'staff'

    @property
    def name(self):
        return self.user.get_full_name()
    
    @property
    def email(self):
        return self.user.email

    def __str__(self):
        return self.user.get_full_name()