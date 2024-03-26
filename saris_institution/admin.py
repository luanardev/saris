from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from .models import *


class CampusAdminMixin:

    def get_campus(self, request):
        return request.user.staff.campus

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            campus = self.get_campus(request)
            return qs.filter(campus=campus)


class DepartmentAdminMixin:

    def get_department(self, request):
        return request.user.staff.department
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            # Superuser sees all models
            return qs
        else:
            # Filter models based on user's department
            department = self.get_department(request)
            return qs.filter(department=department)        
        

class UniversityAdmin(ExportActionModelAdmin):
    list_display = ['name', 'acronym', 'postal_address', 'physical_address', 'email_address', 'telephone_one', 'city', 'country']
    list_display_links = ['name',]
    search_fields = ['name',]

class CampusAdmin(ExportActionModelAdmin):
    list_display = ['code', 'name', 'postal_address', 'email_address', 'phone_number']
    list_display_links = ['name',]
    search_fields = ['name',]

class FacultyAdmin(ExportActionModelAdmin):
    list_display = ['code', 'name', 'campus']
    list_display_links = ['name',]
    search_fields = ['name',]
    list_filter = ['campus']

class DepartmentAdmin(ExportActionModelAdmin):
    list_display = ['code', 'name', 'faculty']
    list_display_links = ['name',]
    search_fields = ['name',]
    list_filter = ['faculty']

class VenueAdmin(CampusAdminMixin, ExportActionModelAdmin):
    list_display = ['name', 'campus']
    list_display_links = ['name',]
    search_fields = ['name',]
    list_filter = ['campus']

admin.site.register(University, UniversityAdmin)
admin.site.register(Campus, CampusAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Venue, VenueAdmin)