import tablib
from slugify import slugify
from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse
from django.views.generic import TemplateView, FormView, DetailView, DeleteView
from django_tables2.views import SingleTableMixin, SingleTableView
from django_tables2.paginators import LazyPaginator
from django_tables2.export import ExportMixin
from django_filters.views import FilterView
from saris.utils import download, get_template_name, get_file_path, show_error, show_success
from saris_admission.filters import EnrollmentSearch
from saris_admission.models import Enrollment
from saris_students.models import Student
from account.mixins import StaffMixin, StaffRequiredMixin
from .apps import SarisBillingConfig
from .mixins import BrowseInvoiceByCampus
from .services import InvoicePayment, MultipleInvoiceGenerator, StudentWallet, InvoiceGenerator
from .resources import TransactionResource
from .models import Transaction, Invoice, TransactionType
from .forms import BulkInvoiceCreateForm, InvoiceCreateForm, CreditForm, DebitForm, ImportForm
from .tables import TransactionTable, InvoiceTable
from .filters import InvoiceFilter, InvoiceSearch

APP_NAME = SarisBillingConfig.name
REDIRECT_URL = "billing:home"


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('index.html', APP_NAME)


class CreateInvoiceView(StaffRequiredMixin, FormView):
    template_name = get_template_name('invoice/create.html', APP_NAME)
    form_class = InvoiceCreateForm
    model = Invoice
        
    def form_valid(self, form):
        try:
            student_number = form.cleaned_data["student_number"]
            service = form.cleaned_data["service"]
            
            generator = InvoiceGenerator(
                student_number=student_number, 
                service=service
            )
            invoice = generator.create()
            messages.success(self.request, "Invoice created")
            return redirect(reverse("billing:invoice.details", args=[invoice.pk]))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class CreateBulkInvoiceView(StaffRequiredMixin, StaffMixin, FormView):
    template_name = get_template_name('invoice/bulk_create.html', APP_NAME)
    form_class = BulkInvoiceCreateForm
    model = Invoice
        
    def form_valid(self, form):
        try:
            service = form.cleaned_data["service"]
            campus = self.get_campus()
            
            generator = MultipleInvoiceGenerator(service, campus)
            generator.create()
            messages.success(self.request, "Multiple invoices created")
            return redirect(reverse("billing:invoice.browse"))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class InvoiceListView(StaffRequiredMixin, SingleTableMixin, BrowseInvoiceByCampus, ExportMixin, FilterView):
    template_name = get_template_name('invoice/browse.html', APP_NAME)
    model = Invoice
    table_class = InvoiceTable
    filterset_class = InvoiceFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    export_formats = ['xlsx']
    export_name = 'invoice_export'
    reset_filter_url = 'billing:invoice.browse'
    
    def get_export_filename(self, export_format):
        prefix = self.request.user.staff.campus
        file_name = slugify(f"{prefix}_{self.export_name}")
        return f"{file_name.upper()}.{export_format}"
  
  
class InvoiceDetailsView(StaffRequiredMixin, DetailView):
    template_name = get_template_name('invoice/details.html', APP_NAME)
    model = Invoice
    context_object_name = 'invoice'
    
    def get_payments(self):
        invoice = self.get_object()
        trans_type = TransactionType.DEBIT
        payments = Transaction.objects.filter(reference=invoice.invoice_number, trans_type=trans_type)
        return payments
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payments = self.get_payments()
        context["payments"] = payments
        return context   


class SearchInvoiceView(StaffRequiredMixin, FilterView):
    template_name = get_template_name('invoice/search.html', APP_NAME)
    model = Invoice
    filterset_class = InvoiceSearch
    reset_filter_url = 'billing:invoice.search'


class CancelInvoiceView(StaffRequiredMixin, DeleteView):
    template_name = get_template_name('invoice/cancel.html', APP_NAME)
    model = Invoice
        
    def post(self, request, *args, **kwargs):
        invoice = self.get_object()
        try:
            manager = InvoicePayment(invoice)
            manager.cancel_invoice()
            message = "Invoice cancelled"
            return show_success(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
 
       
class InvoicePaymentView(StaffRequiredMixin, FormView):
    
    def post(self, request, *args, **kwargs):
        invoice = request.POST.get("id")
        try:
            manager = InvoicePayment(invoice)
            manager.make_payment()
            message = "Payment successful"
            return show_success(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )

  
class CreditStudentView(StaffRequiredMixin, FormView):
    template_name = get_template_name('transaction/credit.html', APP_NAME)
    form_class = CreditForm
    model = Transaction

    def form_valid(self, form):
        try:
            student_number = form.cleaned_data['student_number']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            currency = form.cleaned_data['currency']
            trans_mode = form.cleaned_data['trans_mode']
            
            wallet = StudentWallet(student_number)
            wallet.credit(amount=amount, currency=currency, trans_mode=trans_mode, description=description)
            message = f"Student has been credited with {currency} {amount}"
            return show_success(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )

       
class DebitStudentView(StaffRequiredMixin, FormView):
    template_name = get_template_name('transaction/debit.html', APP_NAME)
    form_class = DebitForm
    model = Transaction

    def form_valid(self, form):
        try:
            invoice_number = form.cleaned_data['invoice_number']
            
            invoice = Invoice.get_by_invoice_number(invoice_number)
            manager = InvoicePayment(invoice)
            manager.make_payment()

            message = f"Student has been debited with {invoice.invoice_amount}"
            return show_success(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )

          
class SearchWalletView(StaffRequiredMixin, FilterView):
    template_name = get_template_name('wallet/search.html', APP_NAME)
    model = Enrollment
    filterset_class = EnrollmentSearch
    reset_filter_url = 'billing:wallet.search'


class WalletView(StaffRequiredMixin, SingleTableView):
    template_name = get_template_name('wallet/browse.html', APP_NAME)
    model = Transaction
    table_class = TransactionTable
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    
    def get_student(self, **kwargs):
        pk=self.kwargs['pk']
        student = Student.objects.get(pk=pk)
        return student
    
    def get_context_data(self, **kwargs):
        student = self.get_student(**kwargs)
        context = super().get_context_data(**kwargs)
        context["student"] = student
        context["wallet"] = StudentWallet(student.student_number)
        return context
    
    def get_queryset(self, **kwargs):
        student = self.get_student(**kwargs)
        queryset = super().get_queryset()
        queryset = queryset.filter(student=student).order_by('-created_at')
        return queryset


class ImportTransactionView(StaffRequiredMixin, FormView):
    template_name = get_template_name('transaction/import.html', APP_NAME)
    form_class = ImportForm

    def form_valid(self, form):
        file = form.cleaned_data["file"]
        result = None
        try:
            dataset = tablib.Dataset().load(file)
            resource = TransactionResource()
            result = resource.import_data(dataset=dataset, raise_errors=True)
            messages.success(self.request, "Operation successful")
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )

        context = super().get_context_data()
        context['form'] = form
        context['result'] = result

        return render(self.request, self.template_name, context)


class ExcelTemplateView(StaffRequiredMixin, TemplateView):
    file_name = get_file_path('downloads/transaction.xlsx', APP_NAME)

    def get(self, request, *args,  **kwargs):
        return download(self.file_name)
