from abc import ABC, abstractmethod
import datetime
from decimal import Decimal
from django.db import models
from saris_admission.models import Enrollment, EnrollmentStatus
from saris_calendar.models import AcademicSemester
from saris_students.models import Student
from .exceptions import (
    InsufficientFundsException,
    InvoiceExistsException, 
    InvoiceNotFoundException,
    OverPaymentException, 
    InvoiceAlreadySettledException,
    TuitionDetailsNotFoundException,
)
from .models import (
    BankAccount, 
    Invoice, 
    InvoiceStatus,
    RemarkFee,
    RepeatCourseFee,
    Service,
    ServiceFee,
    SupplementaryFee, 
    Transaction,
    TransactionMode, 
    TransactionType, 
    TuitionFee
)



class Processor(ABC):
    
    def __init__(self, student_number,  academic_semester = None):
        self.student_number = student_number
        self.student = Student.get_by_student_number(student_number)
        self.enrollment = Enrollment.get_active(student_number)
        self.program = self.enrollment.program
        self.campus = self.enrollment.campus

        if not academic_semester:
            self.academic_semester = self._get_academic_semester()
        elif isinstance(academic_semester, AcademicSemester):
            self.academic_semester = academic_semester
        else:
            self.academic_semester = AcademicSemester.get_by_id(academic_semester)   

        self.previous_academic_semester = AcademicSemester.get_previous(self.campus)

        self.semester = self.enrollment.semester

    def _get_academic_semester(self):
        if not self.campus:
            return None
        elif AcademicSemester.has_active(self.campus):
            return AcademicSemester.get_active(self.campus)
        else:
            return None
    
    @abstractmethod
    def process(self):
        pass


class TuitionManager(object):

    def __init__(self, enrollment: Enrollment):
        self.enrollment = enrollment

    def get_bank_account(self) -> BankAccount:
        return BankAccount.get_by_campus(self.enrollment.campus)

    def get_tuition_fee(self) -> TuitionFee:
        tuition = TuitionFee.objects.filter(
            campus=self.enrollment.campus,
            intake_type=self.enrollment.intake_type,
            program_level=self.enrollment.program.program_level
        ).first()
        if not tuition:
            raise TuitionDetailsNotFoundException
        return tuition


class StudentWallet(object):

    def __init__(self, student_number):
        self.student_number = student_number
        self.student = Student.get_by_student_number(student_number)
        self.enrollment = Enrollment.get_active(student_number)

    def _update_invoice(self, invoice_id):
        invoice = Invoice.get_by_id(invoice_id)
        invoice.change_payment_status()  

    def _check_invoice(self, invoice_id):
        invoice = Invoice.get_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundException
        return invoice

    def _check_debit(self, amount):
        if self.cannot_debit(amount):
            raise InsufficientFundsException

    def _check_payment(self, invoice_amount, payment_amount):
        invoice_amount = Decimal(invoice_amount)
        payment_amount = Decimal(payment_amount)
        if payment_amount > invoice_amount:
            raise OverPaymentException
        
    def _make_payments(self):
        try:
            invoice_tracker = InvoiceTracker(self.student_number)
            invoice_tracker.settle_invoices()
        except:
            pass

    def check_balance(self):
        if not self.has_balance():
            raise InsufficientFundsException

    def credit(self, amount, currency, trans_mode, reference=None, description=None) -> Transaction:
        trans_type = TransactionType.CREDIT

        transaction = Transaction()
        transaction.student = self.student
        transaction.amount = amount
        transaction.currency = currency
        transaction.trans_date = datetime.date.today()
        transaction.trans_type = trans_type
        transaction.trans_mode = trans_mode

        if reference:
            transaction.reference = reference

        if description:
            transaction.description = str(description).upper()
        else:
            transaction.credit_description()
        
        transaction.save()

        self._make_payments()

        return transaction

    def debit(self, amount, currency, trans_mode, reference=None, description=None) -> Transaction:
        invoice = self._check_invoice(reference)
        self._check_payment(invoice.invoice_amount, amount)
        self._check_debit(amount)

        trans_type = TransactionType.DEBIT

        transaction = Transaction()
        transaction.student = self.student
        transaction.amount = amount
        transaction.currency = currency
        transaction.trans_date = datetime.date.today()
        transaction.trans_type = trans_type
        transaction.trans_mode = trans_mode

        if reference :
            transaction.reference = reference

        if description:
            transaction.description = str(description).upper()
        else:
            transaction.debit_decription()

        transaction.save()

        self._update_invoice(reference)

        return transaction

    def get_total_credit(self):
        trans_type = TransactionType.CREDIT
        student = self.student
        result = Transaction.objects.filter(
            student=student, trans_type=trans_type).aggregate(total_sum=models.Sum('amount'))
        total_credit = result['total_sum'] if result['total_sum'] is not None else 0
        return total_credit

    def get_total_debit(self):
        trans_type = TransactionType.DEBIT
        student = self.student
        result = Transaction.objects.filter(
            student=student, trans_type=trans_type).aggregate(total_sum=models.Sum('amount'))
        total_debit = result['total_sum'] if result['total_sum'] is not None else 0
        return total_debit

    def get_balance(self):
        credit = self.get_total_credit()
        debit = self.get_total_debit()
        return Decimal(credit) - Decimal(debit)

    def can_debit(self, amount):
        balance = self.get_balance()
        amount = Decimal(amount)
        if balance >= amount:
            return True
        else:
            return False
        
    def cannot_debit(self, amount):
        return not self.can_debit(amount)

    def has_balance(self):
        balance = self.get_balance()
        if balance > 0:
            return True
        else:
            return False


class InvoicePayment(object):
    
    def __init__(self, invoice):
        if isinstance(invoice, Invoice):
            self.invoice = invoice
        else:
            self.invoice = Invoice.get_by_id(invoice)
        self.student_number = self.invoice.enrollment.student.student_number
    
    def cancel_invoice(self):
        if self.invoice.is_pending():
            self.invoice.delete()
        if self.invoice.is_paid() or self.invoice.is_partial():
            try:
                Transaction.objects.filter(reference=self.invoice.pk).delete()
            except:
                pass
            self.invoice.delete()

    def make_payment(self):
        if self.invoice.is_paid():
            raise InvoiceAlreadySettledException
        
        trans_mode = TransactionMode.AUTO_DEBIT
        reference = self.invoice.pk
        amount = self.invoice.balance
        description = self.invoice.service
        currency = self.invoice.currency

        wallet = StudentWallet(self.student_number)
        transaction = wallet.debit(amount=amount, currency=currency, trans_mode=trans_mode, reference=reference, description=description)
        
        return transaction


class InvoiceGenerator(object):

    def __init__(self, student_number, service, quantity=1, instant_payment=True) -> None:
        self.student = Student.get_by_student_number(student_number)
        self.enrollment = Enrollment.get_active(student_number)
        self.academic_semester = AcademicSemester.get_active(self.enrollment.campus)
        self.service = self._get_service(service)
        self.quantity = quantity
        self.amount = self._get_invoice_amount()
        self.instant_payment = instant_payment
    
    def _get_invoice_amount(self):
        if self.service.name == TuitionFee.SERVICE:
            return self._get_tuition_fee()
        else:
            return self._get_service_fee()

    def _get_service_fee(self):
        service_fee = ServiceFee.get_service_fee(self.service, self.enrollment.campus)
        if service_fee:
            return service_fee.amount
    
    def _get_tuition_fee(self):
        manager = TuitionManager(self.enrollment)
        tuition_fee = manager.get_tuition_fee()
        return tuition_fee.amount

    def _get_service(self,service):
        if isinstance(service, Service):
            return service
        else:
            return Service.get_by_id(service)

    def _make_payment(self, invoice):
        try:
            payment = InvoicePayment(invoice)
            payment.make_payment()
        except:
            pass

    def create(self) -> Invoice:
        invoice_amount = self.quantity * self.amount
        invoice = Invoice()
        invoice.service = self.service
        invoice.enrollment = self.enrollment
        invoice.academic_semester = self.academic_semester
        invoice.invoice_amount = invoice_amount
        invoice.invoice_date = datetime.date.today()
        invoice.status = InvoiceStatus.PENDING
        invoice.save()

        if self.instant_payment:
           self._make_payment(invoice)

        return invoice
    
    def preview(self) -> Invoice:
        invoice_amount = self.quantity * self.amount
        invoice = Invoice()
        invoice.service = self.service
        invoice.enrollment = self.enrollment
        invoice.academic_semester = self.academic_semester
        invoice.invoice_amount = invoice_amount
        invoice.invoice_date = datetime.date.today()
        invoice.status = InvoiceStatus.PENDING
        return invoice


class MultipleInvoiceGenerator(object):

    def __init__(self, service,  campus) -> None:
        self.campus = campus
        self.academic_semester = AcademicSemester.get_active(campus)
        self.service = service

    def _get_enrollments(self):
        status = EnrollmentStatus.ENROLLED
        enrollments = Enrollment.objects.filter(
            status=status,
            campus=self.campus
        )
        return enrollments
    
    def _create(self, enrollment: Enrollment) -> Invoice:
        invoice = InvoiceGenerator(enrollment.student_number, self.service)
        invoice.create()
    
    def create(self):
        enrollments = self._get_enrollments()
        if enrollments.exists():
            for enrollment in enrollments:
                self._create(enrollment)


class InvoiceTracker(object):
    
    def __init__(self, student_number) -> None:
        self.student_number = student_number
        self.student = Student.get_by_student_number(student_number)
        self.enrollment = Enrollment.get_active(student_number)

    def get_invoices(self):
        enrollment = self.enrollment
        return Invoice.objects.filter(enrollment=enrollment)

    def get_outstanding_invoices(self):
        enrollment = self.enrollment
        status = [InvoiceStatus.PENDING, InvoiceStatus.PARTIAL]
        return Invoice.objects.filter(enrollment=enrollment, status__in=status)
    
    def get_settled_invoices(self):
        enrollment = self.enrollment
        status = InvoiceStatus.PAID
        return Invoice.objects.filter(enrollment=enrollment, status=status)
    
    def get_outstanding_invoice(self, service):
        enrollment = self.enrollment
        status = [InvoiceStatus.PENDING, InvoiceStatus.PARTIAL]
        invoice = Invoice.objects.filter(enrollment=enrollment, service=service, status__in=status).first()
        if not invoice:
            raise InvoiceNotFoundException
        return invoice
    
    def get_total_invoice(self):
        status = [InvoiceStatus.PENDING, InvoiceStatus.PARTIAL]
        enrollment = self.enrollment
        result = Invoice.objects.filter(enrollment=enrollment, status__in=status).aggregate(
            total_sum=models.Sum('invoice_amount'))
        total_amount = result['total_sum'] if result['total_sum'] is not None else 0
        return total_amount

    def get_total_payment(self):
        invoices = self.get_outstanding_invoices()
        total_payment = 0
        for invoice in invoices:
            total_payment += invoice.paid_amount
        return total_payment

    def get_total_balance(self):
        invoices = self.get_outstanding_invoices()
        total_balance = 0
        for invoice in invoices:
            total_balance += invoice.balance
        return total_balance

    def has_outstanding_balance(self):
        total_balance = self.get_total_balance()
        if total_balance > 0:
            return True
        else:
            return False

    def settle_invoices(self):
        wallet = StudentWallet(self.student_number)
        total_amount = self.get_total_balance()

        if total_amount > 0:
            if wallet.cannot_debit(total_amount):
                raise InsufficientFundsException  
        
            invoices = self.get_outstanding_invoices()
            for invoice in invoices:
                manager = InvoicePayment(invoice)
                manager.make_payment()


class BaseInvoice(Processor):
    
    def __init__(self, student_number, academic_semester= None):
        super().__init__(student_number, academic_semester)
        self.invoice_tracker = InvoiceTracker(student_number)
        self.wallet = StudentWallet(student_number)
        self.quantity = 1
        self.installment_percent = None
        
    def _queryset(self):
        service = self.get_service()
        enrollment = self.enrollment
        academic_semester = self.academic_semester
        status = [InvoiceStatus.PENDING, InvoiceStatus.PAID]

        return Invoice.objects.filter(
            enrollment=enrollment,
            academic_semester=academic_semester,
            service=service,
            status__in=status
        )

    def get_outstanding_invoices(self):
        return self.invoice_tracker.get_outstanding_invoices()      
    
    def get_outstanding_balance(self):
        return self.invoice_tracker.get_total_balance()
    
    def get_total_amount(self):
        amount = self.get_amount()
        quantity = self.get_quantity()
        return amount * quantity

    def get_service(self):
        service_name = self.get_service_name()
        return Service.get_by_name(service_name)

    def get_service_fee(self):
        service = self.get_service()
        return ServiceFee.get_service_fee(service, self.campus)
    
    def get_amount(self):
        service_fee = self.get_service_fee()
        if service_fee:
            return service_fee.amount
    
    def get_quantity(self):
        return self.quantity
    
    def get_installment_percent(self):
        return self.installment_percent

    def set_quantity(self, quantity):
        self.quantity = quantity

    def set_installment_percent(self, installment_percent):
        self.installment_percent = installment_percent

    def create(self) -> Invoice:
        if not self.exists():
            student_number = self.student_number
            service = self.get_service()
            quantity = self.get_quantity()
            generator = InvoiceGenerator(
                student_number=student_number,
                service=service,
                quantity=quantity,
                instant_payment=False
            )
            return generator.create()

    def preview(self) -> Invoice:
        student_number = self.student_number
        service = self.get_service()
        quantity = self.get_quantity()
        generator = InvoiceGenerator(
            student_number=student_number,
            service=service,
            quantity=quantity
        )
        return generator.preview()

    def fetch(self) -> Invoice:
        return self._queryset().first()

    def cancel(self):
        invoice = self.fetch()
        if invoice:
            manager = InvoicePayment(invoice)
            manager.cancel_invoice()

    def check_invoice(self):
        if self.exists():
            raise InvoiceExistsException
     
    def pre_check_payment(self):
        preview = self.preview()
        if self.wallet.cannot_debit(preview.invoice_amount):
            raise InsufficientFundsException

    def has_installment(self):
        return self.installment_percent is not None

    def is_paid(self):
        invoice = self.fetch()
        return invoice.is_paid()

    def exists(self):
        return self._queryset().exists()
   
    def process(self):
        invoice = self.fetch()
        manager = InvoicePayment(invoice)
        manager.make_payment()

    @abstractmethod
    def get_service_name(self):
        pass

   
class TuitionInvoice(BaseInvoice):

    def __init__(self, student_number, academic_semester=None):
        super().__init__(student_number, academic_semester)

    def get_service_name(self):
        return TuitionFee.SERVICE
      
    def get_amount(self):
        manager = TuitionManager(self.enrollment)
        tuition_fee = manager.get_tuition_fee()
        return tuition_fee.amount
   
    def get_installment(self):
        amount = self.get_amount()
        percent = self.get_installment_percent()
        required_amount = (percent/100) * float(amount)
        return required_amount
    
    def pre_check_payment(self):
        installment = self.get_installment()
        if self.wallet.cannot_debit(installment):
            raise InsufficientFundsException

    def process(self):
        installment = self.get_installment()

        wallet_balance = self.wallet.get_balance()
        tuition_amount = self.get_amount()
        payment_amount = None
        if wallet_balance >= tuition_amount:
           payment_amount = tuition_amount
        else:
            payment_amount = installment

        invoice = self.fetch()
        invoice.invoice_amount = payment_amount
        manager = InvoicePayment(invoice)
        manager.make_payment()


class RFCInvoice(BaseInvoice):
    
    def __init__(self, student_number, academic_semester=None):
        super().__init__(student_number, academic_semester)  
     
    def get_service_name(self):
        return RepeatCourseFee.SERVICE
            

class SUPInvoice(BaseInvoice):
    
    def __init__(self, student_number, academic_semester=None):
        super().__init__(student_number, academic_semester)

    def get_service_name(self):
        return SupplementaryFee.SERVICE
    

class RemarkInvoice(BaseInvoice):
    
    def __init__(self, student_number, academic_semester=None):
        super().__init__(student_number, academic_semester)

    def get_service_name(self):
        return RemarkFee.SERVICE
    
 
   