from django.contrib import admin
from import_export.admin import ExportActionModelAdmin

from saris_institution.admin import CampusAdminMixin
from .models import *


class EnrollmentAdmin(CampusAdminMixin, ExportActionModelAdmin):
    list_display = [
        'student_number', 'student', 'program', 'campus', 'intake_type', 'academic_year', 
        'sponsorship_type', 'semester', 'initial_semester', 'status', 
        'is_compensated', 'is_graduating', 'is_certified',
        'award_name', 'award_class', 'award_level', 'award_gpa'
    ]
    list_display_links = ['student_number','student']
    list_filter = ['campus', 'academic_year', 'semester', 'program', 'status']
    search_fields = ['student__student_number']


class WithdrawalTypeAdmin(ExportActionModelAdmin):
    list_display = ['name', 'period']
    list_display_links = ['name']


class WithdrawalAdmin(ExportActionModelAdmin):
    list_display = ['enrollment', 'academic_semester', 'semester', 'withdrawal_type',  'status']
    list_display_links = ['enrollment', 'academic_semester']
    list_filter = ['academic_semester', 'semester', 'status']
    search_fields = ['enrollment__student__student_number']


admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(WithdrawalType, WithdrawalTypeAdmin)
admin.site.register(Withdrawal, WithdrawalAdmin)