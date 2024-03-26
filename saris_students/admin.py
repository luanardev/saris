from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from .models import *


class StudentAdmin(ExportActionModelAdmin):
    list_display = [
        'student_number', 'title', 'first_name', 'last_name', 'gender', 'date_of_birth', 'marital_status', 
        'email_address', 'phone_number', 'country'
    ]
    list_display_links = ['student_number', 'first_name', 'last_name']
    search_fields = ['student_number', 'first_name', 'last_name']
    list_filter = ['gender', 'marital_status', 'country']


admin.site.register(Student, StudentAdmin)
admin.site.register(Kinsman)