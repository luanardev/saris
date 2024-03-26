from django import forms
from django.core.validators import FileExtensionValidator
from .models import Currency, Invoice, Service, Transaction, TransactionMode


class InvoiceCreateForm(forms.ModelForm):
    student_number = forms.IntegerField(required=True, label="Student number")
    service = forms.ModelChoiceField(queryset=Service.get_all(), label="Service")
    
    class Meta:
        model = Invoice
        fields = ['student_number', 'service']
        exclude = ['enrollment', 'status', 'invoice_date', 'invoice_amount', 'academic_semester']


class BulkInvoiceCreateForm(forms.ModelForm):
    service = forms.ModelChoiceField(queryset=Service.get_all(), label="Service")
    
    class Meta:
        model = Invoice
        fields = ['service' ]
        exclude = ['student_number', 'enrollment', 'status', 'invoice_date', 'invoice_amount', 'academic_semester']


class CreditForm(forms.ModelForm):
    student_number = forms.IntegerField(required=True, label="Student number")
    amount = forms.DecimalField(required=True, label="Amount")
    description = forms.CharField(required=False, initial=None, label="Description")
    currency = forms.ChoiceField(choices=Currency.choices, label="Currency")
    trans_mode = forms.ChoiceField(choices=TransactionMode.choices, label="Transaction Mode")

    class Meta:
        model = Transaction
        fields = ['student_number', 'amount', 'currency', 'trans_mode', 'description']


class DebitForm(forms.ModelForm):
    invoice_number = forms.IntegerField(required=True, label="Invoice number")

    class Meta:
        model = Transaction
        fields = ['invoice_number']


class ImportForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}),
        required=True,
        label="Excel File",
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        help_text="Upload Excel sheet"
    )
