from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from .models import User, Staff


class StaffInline(admin.StackedInline):
    model = Staff
    can_delete = False
    verbose_name_plural = "staff"


class UserAdmin(ExportActionModelAdmin):
    inlines = [StaffInline]
    list_display = ['email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_student']
    list_display_links = ['email',]
    search_fields = ['email', 'first_name', 'last_name',]


admin.site.register(User, UserAdmin)
admin.site.register(Staff)
