from django.contrib import admin
from import_export.admin import ExportActionModelAdmin

from saris_institution.admin import CampusAdminMixin
from .models import *


class RegistrationAdmin(ExportActionModelAdmin):
    list_display = [
        'enrollment', 'academic_semester', 'semester', 'type', 'status',
    ]
    list_display_links = ['enrollment', 'academic_semester']
    search_fields = ['enrollment__student__student_number']
    list_filter = ['academic_semester', 'semester', 'type', 'status']


class RegistrationPolicyAdmin(CampusAdminMixin, ExportActionModelAdmin):
    list_display = [
        'campus', 'registration_installment', 'examination_installment', 'results_installment',
        'block_registration', 'block_examination', 'block_results'
    ]
    list_display_links = ['campus']
    list_filter = ['campus']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            campus = self.get_campus(request)
            return qs.filter(campus=campus)


admin.site.register(Registration, RegistrationAdmin)
admin.site.register(RegistrationPolicy, RegistrationPolicyAdmin)
