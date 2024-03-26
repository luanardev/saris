import locale
import django_tables2 as tables
from .models import Invoice, Transaction


class CustomNumberColumn(tables.Column):
    def __init__(self, verbose_name=None, accessor=None, default=None, visible=True, orderable=None, attrs=None, order_by=None, empty_values=None, localize=None, footer=None, exclude_from_export=False, linkify=False, initial_sort_descending=False):
        super().__init__(verbose_name, accessor, default, visible, orderable, attrs, order_by, empty_values, localize, footer, exclude_from_export, linkify, initial_sort_descending)
        
    def render(self, value):
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            formatted_value = locale.format_string("%d", value, grouping=True)
            return formatted_value
        except (ValueError, TypeError):
            return value


class InvoiceTable(tables.Table):
    invoice_number = tables.Column(
        verbose_name="INVOICE NO",
        accessor="invoice_number",
        linkify=("billing:invoice.details", [tables.A("pk")])
    )
    
    student_number = tables.Column(
        verbose_name="STUDENT NO",
        accessor="enrollment__student__student_number"
    )
    
    student = tables.Column(
        verbose_name="STUDENT NAME",
        accessor="enrollment__student",
    )
    
    service = tables.Column(
        verbose_name="SERVICE",
        accessor="service",
    )
    
    invoice_amount = CustomNumberColumn(
        verbose_name="INVOICE AMOUNT",
        accessor="invoice_amount",
    )

    paid_amount = CustomNumberColumn(
        verbose_name="PAID AMOUNT",
        accessor="paid_amount",
    )

    balance = CustomNumberColumn(
        verbose_name="BALANCE",
        accessor="balance",
    )
    
    academic_semester = tables.Column(
        verbose_name="SESSION",
        accessor="academic_semester",
    )

    class Meta:
        model = Invoice
        fields = [
            'invoice_number','student_number', 'student', 'service', 
            'invoice_amount', 'paid_amount', 'balance', 'academic_semester',
        ]


class TransactionTable(tables.Table):
   
    trans_date = tables.DateColumn(
        format="d-M-Y",
        verbose_name="DATE",
        accessor="trans_date",
    )
    
    trans_type = tables.Column(
        verbose_name="TRANS TYPE",
        accessor="trans_type",
    )

    trans_mode = tables.Column(
        verbose_name="TRANS MODE",
        accessor="trans_mode",
    )
    
    amount = CustomNumberColumn(
        verbose_name="AMOUNT",
        accessor="amount",
    )

    currency = CustomNumberColumn(
        verbose_name="CURRENCY",
        accessor="currency",
    )
    
    description = tables.Column(
        verbose_name="DESCRIPTION",
        accessor="description",
    )

    
    class Meta:
        model = Transaction
        fields = ['trans_date', 'description',  'amount', 'currency',  'trans_type',  'trans_mode',]
