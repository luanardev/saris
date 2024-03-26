from django.contrib import admin

from .models import Transfer, Stage, Approver, Approval


class ApproverAdmin(admin.ModelAdmin):
    list_display = ['stage', 'group']
    list_display_links = ['stage', 'group']
    search_fields = ['stage', 'group']


class TransferAdmin(admin.ModelAdmin):
    list_display = [
        'enrollment', 'academic_semester', 'transfer_type', 'stage', 'new_program', 'new_campus',
        'request_status', 'request_date', 'approval_status', 'approval_date'
    ]
    list_display_links = ['enrollment', 'academic_semester']
    search_fields = ['enrollment__student__student_number']
    list_filter = ['academic_semester', 'transfer_type', 'request_status', 'approval_status']


class ApprovalAdmin(admin.ModelAdmin):
    list_display = ['transfer', 'stage', 'decision', 'comment', 'approval_date', 'approver']
    list_display_links = ['transfer', 'stage']
    search_fields = ['transfer', 'stage']


class StageAdmin(admin.ModelAdmin):
    list_display = ['name', 'level']
    list_display_links = ['name', 'level']


admin.site.register(Approver, ApproverAdmin)
admin.site.register(Transfer, TransferAdmin)
admin.site.register(Approval, ApprovalAdmin)
admin.site.register(Stage, StageAdmin)
