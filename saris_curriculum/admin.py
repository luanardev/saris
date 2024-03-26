from django.contrib import admin
from import_export.admin import ExportActionModelAdmin

from .models import *


class ProgramAdmin(ExportActionModelAdmin):
    list_display = ['code', 'name', 'field_name', 'version', 'semesters', 'years',
       'program_type','program_level', 'department', 'status'
    ]
    list_display_links = ['code']
    search_fields = ['code', 'name']
    list_filter = ['program_type', 'program_level', 'department', 'status']


class CourseAdmin(ExportActionModelAdmin):
    list_display = ['code', 'name', 'version', 'credit_hours', 'department', 'status']
    list_display_links = ['code']
    search_fields = ['code', 'name']
    list_filter = ['department', 'status']


class MasterCurriculumAdmin(ExportActionModelAdmin):
    list_display = ['program', 'course', 'course_type', 'semester', 'version']
    list_display_links = ['program', 'course']
    list_filter = ['program',  'semester']
    search_fields = ['program__code', 'course__code']


class ConfiguredCurriculumAdmin(ExportActionModelAdmin):
    list_display = ['academic_semester', 'program', 'semester', 'version']
    list_display_links = ['academic_semester', 'program']
    list_filter = ['academic_semester', 'program', 'semester', 'version']


class ConfiguredCourseAdmin(ExportActionModelAdmin):
    list_display = ['curriculum',  'course', 'course_type', 'semester']
    list_display_links = ['curriculum', 'course']


admin.site.register(Program, ProgramAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(MasterCurriculum, MasterCurriculumAdmin)
admin.site.register(ConfiguredCurriculum, ConfiguredCurriculumAdmin)
admin.site.register(ConfiguredCourse, ConfiguredCourseAdmin)

