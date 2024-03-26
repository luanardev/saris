from django.contrib import admin

from saris_institution.admin import CampusAdminMixin
from .models import *

# Register your models here.
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['code', 'start_year','end_year','status']
    list_display_links = ['code',]
    search_fields = ['code',]


class AcademicActivityAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    list_display_links = ['code',]
    search_fields = ['code', 'name']


class AcademicSemesterAdmin(CampusAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'semester', 'start_date', 'end_date', 'status', 'academic_year', 'campus',]
    list_display_links = ['name',]
    search_fields = ['name',]
    list_filter = ['campus', 'academic_year', 'semester']


class AcademicSemesterActivityAdmin(admin.ModelAdmin):
    list_display = ['academic_semester', 'academic_activity', 'start_date', 'end_date', 'status']
    list_display_links = ['academic_semester', 'academic_activity']
    list_filter = ['academic_semester', 'academic_activity']


admin.site.register(AcademicYear, AcademicYearAdmin)
admin.site.register(AcademicActivity, AcademicActivityAdmin)
admin.site.register(AcademicSemester, AcademicSemesterAdmin)
admin.site.register(AcademicSemesterActivity, AcademicSemesterActivityAdmin)
