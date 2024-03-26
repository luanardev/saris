
from typing import Any
import slugify
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render, resolve_url
from django.urls import reverse
from django.views.generic import TemplateView, FormView, DetailView, DeleteView
from django_tables2 import LazyPaginator, SingleTableView
from dpo import DPOPay, PaymentForm
from saris.mixins import RenderPDFMixin
from saris.utils import get_template_name, show_error, show_success
from account.mixins import StudentRequiredMixin
from saris_admission.models import Withdrawal
from saris_admission.tables import WithdrawalTable
from saris_assessment.exceptions import ExamResultsNotFoundException
from saris_assessment.models import CourseAppeal, StudentCourse, Supplementary
from saris_billing.models import Invoice, Transaction, TransactionMode, TransactionType
from saris_billing.services import InvoicePayment, InvoiceTracker, StudentWallet
from saris_billing.tables import TransactionTable
from saris_studentportal.apps import SarisStudentportalConfig
from saris_studentportal.forms import ChangeCampusForm, ChangeProgramForm, CourseAppealForm
from saris_studentportal.mixins import StudentMixin
from saris_studentportal.services import CourseRemark, GradeCorrection, ResultsAccess, StudentRegistration, ExamPermit, StudentStatement, StudentSupplementary
from saris_studentportal.tables import CourseAppealTable, PaymentTable, StudentCourseTable, InvoiceTable, SupplementaryTable, TransferTable, WithdrawalTable
from saris_transfer.models import Transfer
from saris_transfer.services import CampusTransfer, ProgramTransfer



APP_NAME = SarisStudentportalConfig.name

DPO_VERIFY_PAYMENT_URL = "studentportal:dpo_verify_payment"
DPO_CANCEL_PAYMENT_URL = "studentportal:dpo_cancel_payment"

HOME_URL = "studentportal:home"
WALLET_URL = "studentportal:wallet"
INVOICES_URL = "studentportal:invoices"
REGISTRATION_URL = "studentportal:registration"
EXAMPERMIT_URL = "studentportal:exam_permit"
TRANSFERS_URL = "studentportal:transfers"
WITHDRAWALS_URL = "studentportal:withdrawals"
APPEALS_URL = "studentportal:course_appeals"
SUPPLEMENTARY_URL = "studentportal:supplementary"


class DashboardView(StudentRequiredMixin, StudentMixin, TemplateView):
    template_name = get_template_name('index.html', APP_NAME)


class WalletView(StudentRequiredMixin, StudentMixin, SingleTableView):
    template_name = get_template_name('wallet/index.html', APP_NAME)
    model = Transaction
    table_class = TransactionTable
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    
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


class InvoiceListView(StudentRequiredMixin, StudentMixin, SingleTableView):
    template_name = get_template_name('invoices/index.html', APP_NAME)
    model = Invoice
    table_class = InvoiceTable
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}

    def get_invoice_tracker(self):
        student = self.get_student()
        tracker = InvoiceTracker(student.student_number)
        return tracker
    
    def get_invoices(self, **kwargs):
        tracker = self.get_invoice_tracker()
        invoices = tracker.get_outstanding_invoices()
        return invoices
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice_tracker = self.get_invoice_tracker()
        context["invoice_tracker"] = invoice_tracker
        return context
    
    def get_queryset(self, **kwargs):
        queryset = super().get_queryset()
        invoices = self.get_invoices()
        queryset = invoices
        return queryset


class InvoiceDetailsView(StudentRequiredMixin, DetailView):
    template_name = get_template_name('invoices/invoice.html', APP_NAME)
    model = Invoice
    context_object_name = 'invoice'
    
    def get_payments(self):
        invoice = self.get_object()
        trans_type = TransactionType.DEBIT
        payments = Transaction.filter(reference=invoice.invoice_number, trans_type=trans_type)
        return payments
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payments = self.get_payments()
        context["payments"] = payments
        return context   


class PaymentListView(StudentRequiredMixin, StudentMixin, SingleTableView):
    template_name = get_template_name('invoices/payments.html', APP_NAME)
    model = Invoice
    table_class = PaymentTable
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}

    def get_invoice_tracker(self):
        student = self.get_student()
        tracker = InvoiceTracker(student.student_number)
        return tracker
    
    def get_payments(self, **kwargs):
        tracker = self.get_invoice_tracker()
        invoices = tracker.get_settled_invoices()
        return invoices
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice_tracker = self.get_invoice_tracker()
        context["invoice_tracker"] = invoice_tracker
        return context
    
    def get_queryset(self, **kwargs):
        queryset = super().get_queryset()
        invoices = self.get_payments()
        queryset = invoices
        return queryset


class PaymentDetailsView(InvoiceDetailsView):
    template_name = get_template_name('invoices/payment.html', APP_NAME)

      
class InvoicePaymentView(StudentRequiredMixin, FormView):
    
    def post(self, request, *args, **kwargs):
        invoice = request.POST.get("id")
        try:
            manager = InvoicePayment(invoice)
            manager.make_payment()
            message = "Payment successful"
            return show_success(
                request=self.request,
                message=message,
                redirect_url=INVOICES_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=INVOICES_URL,
                app_name=APP_NAME
            )

  
class DPOCreatePaymentView(StudentRequiredMixin, StudentMixin, FormView):
    template_name = get_template_name('wallet/deposit.html', APP_NAME)
    form_class = PaymentForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student"] = self.get_student()
        return context
    
    def post(self, request, *args, **kwargs):
        
        try:

            student = self.get_student()
            student_number = student.student_number
            amount = request.POST.get('amount')
            description = request.POST.get('description')

            dpo = DPOPay()

            redirect_url= request.build_absolute_uri(resolve_url(DPO_VERIFY_PAYMENT_URL))
            back_url = request.build_absolute_uri(resolve_url(DPO_CANCEL_PAYMENT_URL))

            dpo.set_redirect_url(redirect_url)
            dpo.set_back_url(back_url)

            response = dpo.create_token(
                company_ref=student_number,
                amount=float(amount),
                description=description
            )
            trans_token = response.TransToken

            return dpo.make_payment(trans_token)
    
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=WALLET_URL
            )


class DPOVerifyPaymentView(StudentRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):

        if not request.GET.get('TransID') and not request.GET.get('companyRef'):
            return HttpResponseBadRequest()
        
        try:
            trans_token = request.GET.get('TransID')
            student_number = request.GET.get('PnrID')

            dpo = DPOPay()

            response = dpo.verify_payment(trans_token)

            amount = response.TransactionAmount
            currency = response.TransactionCurrency
            trans_mode = TransactionMode.ELECTRONIC
            
            wallet = StudentWallet(student_number)
            wallet.credit(amount=amount, currency=currency, trans_mode=trans_mode, reference=trans_token)
            
            message=f"Your wallet has been credited with {currency} {amount}"
            messages.success(request, message) 

            return redirect(reverse(WALLET_URL))
            
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=WALLET_URL
            )

   
class DPOCancelPaymentView(StudentRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):

        if not request.GET.get('TransID') and not request.GET.get('companyRef'):
            return HttpResponseBadRequest()
        
        try:

            trans_token = request.GET.get('TransID')
            dpo = DPOPay()
            dpo.cancel_token(trans_token)
            messages.success(request, "Transaction cancelled") 
            return redirect(reverse(WALLET_URL))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=WALLET_URL
            )


class RegistrationView(StudentRequiredMixin, StudentMixin, TemplateView):
    template_name = get_template_name('registration/details.html', APP_NAME)

    def get_register(self):
        student = self.get_student()
        manager = StudentRegistration(student.student_number)
        return manager.get_register()

    def get(self, request, *args, **kwargs):
        try:
            register = self.get_register()
            register.check_withdrawal()
            register.check_completion()

            if register.has_registered():
                registration = register.get_registration()
                context = {"registration": registration}
                return render(request, self.template_name, context)
            else:
                template = get_template_name("registration/create.html", APP_NAME)
                return render(request, template)
        except Exception as message:
            return show_error(
                request=self.request, 
                message=message, 
                redirect_url=HOME_URL,
                app_name=APP_NAME
            )
            
       
class RegisterView(StudentRequiredMixin, StudentMixin, FormView):

    def get_register(self):
        student = self.get_student()
        manager = StudentRegistration(student.student_number)
        return manager.get_register()
        
    def get(self, request, *args, **kwargs):
        try:
            register = self.get_register()
            register.check_withdrawal()
            register.check_completion()
            invoice_manager = register.get_invoice_manager()
            
            context = {"invoice_manager": invoice_manager}
            template = get_template_name("registration/invoice.html", APP_NAME)
            return render(request, template, context)
        
        except Exception as message:
            return show_error(
                request=self.request, 
                message=message, 
                redirect_url=REGISTRATION_URL,
                app_name=APP_NAME
            )
            
      
class RegisterCheckoutView(StudentRequiredMixin, StudentMixin, FormView):
    
    def get_register(self):
        student = self.get_student()
        manager = StudentRegistration(student.student_number)
        return manager.get_register()
    
    def post(self, request, *args, **kwargs):
        try:
            register = self.get_register()
            register.check_withdrawal()
            register.check_completion()
            register.check_duplicate()
            register.process()

            messages.success(request, "Registration successful")    
            return redirect(reverse(REGISTRATION_URL))
        except Exception as message:
            return show_error(
                request=request,
                message=message,
                redirect_url=REGISTRATION_URL,
                app_name=APP_NAME
            )


class ClearBalanceView(StudentRequiredMixin, StudentMixin, FormView):

    def post(self, request, *args, **kwargs):
        try:
            student = self.get_student()
            invoice_tracker = InvoiceTracker(student.student_number)
            invoice_tracker.settle_invoices()
            messages.success(request, "Payment successful")    
            return redirect(reverse(INVOICES_URL))
        except Exception as message:
            return show_error(
                request=request,
                message=message,
                redirect_url=INVOICES_URL,
                app_name=APP_NAME
            )


class CourseListView(StudentRequiredMixin, StudentMixin, SingleTableView):
    template_name = get_template_name('registration/courses.html', APP_NAME)
    model = StudentCourse
    table_class = StudentCourseTable

    def get_register(self):
        student = self.get_student()
        manager = StudentRegistration(student.student_number)
        return manager.get_register()
    
    def get_registration(self, **kwargs):
        register = self.get_register()
        register.check_registration()
        return register.get_registration()
    
    def get_queryset(self, **kwargs):
        registration = self.get_registration(**kwargs)
        queryset = super().get_queryset()
        queryset = queryset.filter(
            enrollment=registration.enrollment,
            academic_semester=registration.academic_semester,
            semester=registration.semester
        )
        return queryset
    
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=HOME_URL,
                app_name=APP_NAME
            )


class ExamPermitView(StudentRequiredMixin, StudentMixin, TemplateView):
    template_name = get_template_name('exam_permit/details.html', APP_NAME)

    def get(self, request, *args, **kwargs):
        try:
            student = self.get_student()

            exam_permit = ExamPermit(student.student_number)
            exam_permit.check_withdrawal()
            exam_permit.check_completion()
            exam_permit.check_registration()
            exam_permit.process()

            context = {"exam_permit": exam_permit}
            return render(request, self.template_name, context)
              
        except Exception as message:
            return show_error(
                request=self.request, 
                message=message, 
                redirect_url=REGISTRATION_URL,
                app_name=APP_NAME
            )
            

class DownloadExamPermitView(StudentRequiredMixin, RenderPDFMixin, StudentMixin, TemplateView):
    template_name = get_template_name('exam_permit/pdf.html', APP_NAME)
    download_name = "Exam_Permit"

    def get_download_name(self, **kwargs):
        file_name = slugify(f"{self.download_name}")
        return f"{file_name.upper()}.pdf"
    
    def get(self, request, *args, **kwargs):
        try:
            student = self.get_student()

            exam_permit = ExamPermit(student.student_number)
            exam_permit.check_withdrawal()
            exam_permit.check_completion()
            exam_permit.check_registration()
            exam_permit.process()

            context = {"exam_permit": exam_permit}
            
            return self.render_pdf(request, self.template_name, context)
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=EXAMPERMIT_URL,
                app_name=APP_NAME
            )


class ExamResultsView(StudentRequiredMixin, StudentMixin, TemplateView):
    template_name = get_template_name('exam_results/results.html', APP_NAME)

    
    def get(self, request, *args, **kwargs):
        try:
            student = self.get_student()
            results_access = ResultsAccess(student.student_number)
            results_access.check_registration()
            results_access.process()

            if results_access.has_no_grades():
                raise ExamResultsNotFoundException
            
            grades = results_access.get_grades()
            summary = results_access.get_summary()
            context = {"grades" : grades, "summary" : summary}

            return render(request, self.template_name, context)

        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=HOME_URL,
                app_name=APP_NAME
            )


class ResultStatementView(StudentRequiredMixin, StudentMixin, TemplateView):
    template_name = get_template_name('exam_results/statement.html', APP_NAME)

    
    def get(self, request, *args, **kwargs):
        try:
            student = self.get_student()
            statement = StudentStatement(student.student_number)
            statement.check_statement()

            context = {"statement" : statement}

            return render(request, self.template_name, context)

        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=HOME_URL,
                app_name=APP_NAME
            )


class ChangeCampusView(StudentRequiredMixin, StudentMixin, FormView):
    template_name = get_template_name('transfer/change_campus.html', APP_NAME)
    form_class = ChangeCampusForm

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        try:
            student = self.get_student()
            manager = StudentRegistration(student.student_number)
            register = manager.get_register()

            register.check_withdrawal()
            register.check_completion()

            return super().get(request, *args, **kwargs)
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=HOME_URL,
                app_name=APP_NAME
            )

    def form_valid(self, form):
        try:
            student =  self.get_student()

            campus = form.cleaned_data["campus"]
            student_number = student.student_number

            transfer = CampusTransfer(student_number, campus)
            transfer.check_transfer()
            transfer.process()
            messages.success(self.request, "Transfer request successful")
            return redirect(reverse(TRANSFERS_URL))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=TRANSFERS_URL,
                app_name=APP_NAME
            )
    

class ChangeProgramView(StudentRequiredMixin, StudentMixin, FormView):
    template_name = get_template_name('transfer/change_program.html', APP_NAME)
    form_class = ChangeProgramForm

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        try:
            student = self.get_student()
            manager = StudentRegistration(student.student_number)
            register = manager.get_register()

            register.check_withdrawal()
            register.check_completion()

            return super().get(request, *args, **kwargs)
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=HOME_URL,
                app_name=APP_NAME
            )

    def form_valid(self, form):
        try:
            student =  self.get_student()
            program = form.cleaned_data["program"]
            student_number = student.student_number

            transfer = ProgramTransfer(student_number, program)
            transfer.check_transfer()
            transfer.process()
            messages.success(self.request, "Transfer request successful")
            return redirect(reverse(TRANSFERS_URL))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=TRANSFERS_URL,
                app_name=APP_NAME
            )
    

class TransferListView(StudentRequiredMixin, StudentMixin, SingleTableView):
    template_name = get_template_name('transfer/index.html', APP_NAME)
    model = Transfer
    table_class = TransferTable
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    

class TransferDetailsView(StudentRequiredMixin, DetailView):
    template_name = get_template_name('transfer/details.html', APP_NAME)
    model = Transfer
    context_object_name = 'transfer'


class CancelTransferView(StudentRequiredMixin, DeleteView):
    template_name = get_template_name('transfer/cancel.html', APP_NAME)
    model = Transfer

    def post(self, request, *args, **kwargs):
        try:
            transfer = self.get_object()
            transfer.delete()
            message = "Transfer request cancelled"
            return show_success(
                request=self.request,
                message=message,
                redirect_url=TRANSFERS_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
               request=self.request,
               message=message,
               redirect_url=TRANSFERS_URL,
               app_name=APP_NAME
            )


class WithdrawaListView(StudentRequiredMixin, StudentMixin, SingleTableView):
    template_name = get_template_name('withdrawal/index.html', APP_NAME)
    model = Withdrawal
    table_class = WithdrawalTable
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}


class WithdrawalDetailsView(StudentRequiredMixin, StudentMixin, DetailView):
    template_name = get_template_name('withdrawal/details.html', APP_NAME)
    model = Withdrawal
    context_object_name = 'withdrawal'


class CourseRemarkView(StudentRequiredMixin, StudentMixin, FormView):
    template_name = get_template_name('appeals/course_remark.html', APP_NAME)
    form_class = CourseAppealForm

    def get_form(self):
        student = self.get_student()
        form = CourseAppealForm(student.student_number)
        return form
    
    def get(self, request, *args, **kwargs):
        try:
            student = self.get_student()
            results_access = ResultsAccess(student.student_number)
            results_access.check_registration()
            results_access.check_results()
            results_access.process()

            return super().get(request, *args, **kwargs)
        except Exception as message:
            return show_error(
               request=self.request,
               message=message,
               redirect_url=APPEALS_URL,
               app_name=APP_NAME
            )

    def post(self, request, *args, **kwargs):
        try:
            student = self.get_student()
            courses = request.POST.getlist("course")

            appeal = CourseRemark(student.student_number)
            appeal.set_courses(courses)

            self.request.session["appeals"] = courses
            self.request.session.save()

            context = {"appeal": appeal}
            template = get_template_name("appeals/courses.html", APP_NAME)
            return render(request, template, context)
        except Exception as message:
            return show_error(
               request=self.request,
               message=message,
               redirect_url=APPEALS_URL,
               app_name=APP_NAME
            )


class CourseRemarkCheckoutView(StudentRequiredMixin, StudentMixin, FormView):
    
    def post(self, request, *args, **kwargs):
        try:
            courses = request.session.get("appeals")
            student = self.get_student()

            appeal = CourseRemark(student.student_number)
            appeal.set_courses(courses)
            appeal.process()

            request.session.delete("appeals")

            messages.success(request, "Course appeal successful")    
            return redirect(reverse(APPEALS_URL))
        except Exception as message:
            appeal.cancel()
            return show_error(
                request=request,
                message=message,
                redirect_url=APPEALS_URL,
                app_name=APP_NAME
            )

   
class CourseRemarkCancelView(StudentRequiredMixin, StudentMixin, FormView):

    def get(self, request, *args, **kwargs):
        try:
            request.session.delete("appeals")
            message = "Course appeal cancelled"
            return show_success(
                request=request,
                message=message,
                redirect_url=APPEALS_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=request,
                message=message,
                redirect_url=APPEALS_URL,
                app_name=APP_NAME
            )


class GradeCorrectionView(CourseRemarkView):
    template_name = get_template_name('appeals/grade_correction.html', APP_NAME)
    
    def post(self, request, *args, **kwargs):
        try:
            student = self.get_student()
            courses = request.POST.getlist("course")

            appeal = GradeCorrection(student.student_number)
            appeal.set_courses(courses)
            appeal.process()

            messages.success(request, "Course appeal successful")    
            return redirect(reverse(APPEALS_URL))

        except Exception as message:
            return show_error(
                request=request,
                message=message,
                redirect_url=APPEALS_URL,
                app_name=APP_NAME
            )


class CourseAppealListView(StudentRequiredMixin, StudentMixin, SingleTableView):
    template_name = get_template_name('appeals/index.html', APP_NAME)
    model = CourseAppeal
    table_class = CourseAppealTable
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}

    def get_queryset(self, **kwargs):
        student = self.get_student()
        queryset = super().get_queryset()
        queryset = queryset.filter(
            enrollment=student.enrollment
        )
        return queryset


class CourseAppealDetailsView(StudentRequiredMixin, StudentMixin, DetailView):
    template_name = get_template_name('appeals/details.html', APP_NAME)
    model = CourseAppeal
    context_object_name = 'courseappeal'

       
class SupplementaryView(StudentRequiredMixin, StudentMixin, SingleTableView):
    template_name = get_template_name("supplementary/courses.html", APP_NAME)
    table_class = SupplementaryTable
    model = Supplementary

    def get_register(self, **kwargs):
        student = self.get_student()
        manager = StudentRegistration(student.student_number)
        return manager.get_register()
    
    def get_registration(self, **kwargs):
        register = self.get_register()
        return register.get_registration()
    
    def get_queryset(self, **kwargs):
        registration = self.get_registration()
        queryset = super().get_queryset()
        queryset = queryset.filter(
            enrollment=registration.enrollment,
            academic_semester=registration.academic_semester,
            semester=registration.semester
        )
        return queryset

    def get(self, request, *args, **kwargs):
        try:
            register = self.get_register()

            if register.is_registered():
                return super().get(request, *args, **kwargs)
            else:
                manager = StudentSupplementary(register.student_number)
                manager.check_supplementary()
                
                invoice_manager = register.get_invoice_manager()
                context = {"invoice_manager": invoice_manager}
                template = get_template_name("supplementary/invoice.html", APP_NAME)
                return render(request, template, context)
        
        except Exception as message:
            return show_error(
                request=self.request, 
                message=message, 
                redirect_url=REGISTRATION_URL,
                app_name=APP_NAME
            )
            

class SupplementaryCheckoutView(StudentRequiredMixin, StudentMixin, FormView):
    
    def get_register(self):
        student = self.get_student()
        manager = StudentRegistration(student.student_number)
        return manager.get_register()
    
    def post(self, request, *args, **kwargs):
        try:
            register = self.get_register()
            register.check_withdrawal()
            register.check_completion()
            register.check_duplicate()
            register.process()

            messages.success(request, "Supplementary registration successful")    
            return redirect(reverse(SUPPLEMENTARY_URL))
        except Exception as message:
            return show_error(
                request=request,
                message=message,
                redirect_url=SUPPLEMENTARY_URL,
                app_name=APP_NAME
            )
 