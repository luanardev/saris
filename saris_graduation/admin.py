from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from .models import *


class CandidateAdmin(ExportActionModelAdmin):
    list_display = ['enrollment', 'session']
    list_display_links = ['enrollment']


class SessionAdmin(ExportActionModelAdmin):
    list_display = ['name', 'academic_year', 'graduation_date']
    list_display_links = ['name']
    list_filter = ['academic_year']


class BookletAdmin(ExportActionModelAdmin):
    list_display = [
        'session', 'status', 'pdf_file'
    ]
    list_display_links = ['session']
    list_filter = ['session']


admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Booklet, BookletAdmin)