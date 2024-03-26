from django.contrib import admin
from import_export.admin import ExportActionModelAdmin

from saris_institution.admin import CampusAdminMixin
from .models import *



class ServiceAdmin(ExportActionModelAdmin):
    list_display = ['name']


class ServiceFeeAdmin(CampusAdminMixin, ExportActionModelAdmin):
    list_display = ['service', 'campus', 'amount', 'currency']
    list_display_links = ['service', 'campus']
    list_filter = ['campus', 'service']


class TuitionFeeAdmin(CampusAdminMixin, ExportActionModelAdmin):
    list_display = ['campus', 'amount', 'currency', 'intake_type', 'program_level', 'tuition_type', 'service']
    list_display_links = ['campus', 'amount']
    list_filter = ['campus', 'service']


class InvoiceAdmin(ExportActionModelAdmin):
    list_display = ['enrollment', 'invoice_number', 'service', 'academic_semester', 'invoice_amount', 'invoice_date', 'status']
    list_display_links = ['enrollment', 'invoice_number']
    search_fields = ['enrollment__student__student_number', 'invoice_number']
    list_filter = ['service', 'status']


class TransactionAdmin(ExportActionModelAdmin):
    list_display = ['student_number', 'student', 'reference', 'trans_type', 'trans_mode', 'description', 'amount', 'currency', 'created_at']
    list_display_links = ['student_number', 'student', 'reference']
    search_fields = ['student__student_number','reference']
    list_filter = ['trans_type', 'trans_mode']
    

class BankAccountAdmin(CampusAdminMixin, ExportActionModelAdmin):
    list_display = ['campus', 'account_number', 'account_name', 'bank_name', 'branch_name']
    list_display_links = ['campus', 'account_number']
    search_fields = ['account_number']
    list_filter = ['campus']


admin.site.register(ServiceFee, ServiceFeeAdmin)
admin.site.register(TuitionFee, TuitionFeeAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(Service, ServiceAdmin)


