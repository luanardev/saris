import uuid
from django.db import models
from saris.models import SarisModel
from saris_calendar.models import AcademicSemester
from saris_institution.models import Campus
from saris_curriculum.models import IntakeType, ProgramLevel
from saris_admission.models import Enrollment
from saris_students.models import Student
from saris.utils import reference_number
from .exceptions import (
    BankDetailsNotFoundException, 
    InvoiceNotFoundException,
    ServiceFeeNotFoundException
)


class InvoiceStatus(models.TextChoices):
    PENDING = 'PENDING'
    PARTIAL = 'PARTIAL'
    PAID = 'PAID'
    CANCELLED = 'CANCELLED'


class TuitionType(models.TextChoices):
    NATIONAL = 'NATIONAL'
    INTERNATIONAL = 'INTERNATIONAL'


class TransactionType(models.TextChoices):    
    CREDIT = 'CREDIT'
    DEBIT = 'DEBIT'


class TransactionMode(models.TextChoices):    
    CASH = 'CASH'
    ELECTRONIC = 'ELECTRONIC'
    BANK_DEPOSIT = 'BANK DEPOSIT'
    AUTO_CREDIT = 'AUTO CREDIT'
    AUTO_DEBIT = 'AUTO DEBIT'
    

class Currency(models.TextChoices):
    MWK = 'MWK'
    USD = 'USD'
    GBP = 'GBP'
    ZAR = 'ZAR'


class BankAccount(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    bank_name = models.CharField(max_length=255)
    branch_name = models.CharField(max_length=255)
    account_number = models.IntegerField()
    account_name = models.CharField(max_length=255)
    campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING)
    
    class Meta:
        verbose_name = 'Bank Account'
        verbose_name_plural = 'bank accounts'
        
    def __str__(self) -> str:
        return self.account_name
    
    @staticmethod
    def get_by_campus(campus):
        bank_account = BankAccount.objects.filter(campus=campus).first()
        if not bank_account:
            raise BankDetailsNotFoundException
        return bank_account


class Service(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.name}"
    
    @staticmethod
    def get_by_name(name):
        service = Service.objects.filter(name=name).first()
        if not service:
            raise Exception(f"{name} service not found")  
        return service


class ServiceFee(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    service = models.ForeignKey(Service, on_delete=models.DO_NOTHING)
    campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    currency = models.CharField(max_length=255, choices=Currency.choices, default=Currency.MWK)

    class Meta:
        verbose_name = 'Service Fee'
        verbose_name_plural = 'service fees'

    def __str__(self) -> str:
        return f"{self.campus.name} - {self.service.name} - {self.amount}"
    
    @staticmethod
    def get_service_fee(service, campus):
        service_fee = ServiceFee.objects.filter(service=service,campus=campus).first()
        if not service_fee:
            raise ServiceFeeNotFoundException
        return service_fee


class TuitionFee(SarisModel):
    SERVICE = 'Tuition'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    currency = models.CharField(max_length=255, choices=Currency.choices, default=Currency.MWK)
    intake_type = models.CharField(max_length=255, choices=IntakeType.choices)
    program_level = models.CharField(max_length=255, choices=ProgramLevel.choices)
    tuition_type = models.CharField(max_length=255, choices=TuitionType.choices)
    service = models.ForeignKey(Service, on_delete=models.DO_NOTHING)
   
    class Meta:
        verbose_name = 'Tuition Fee'
        verbose_name_plural = 'tuition fees'

    def __str__(self):
        return f"{self.campus} - {self.program_level} - {self.intake_type}"


class RepeatCourseFee(ServiceFee):
    SERVICE = 'Repeat Course'
    class Meta:
        proxy = True


class RemarkFee(ServiceFee):
    SERVICE = 'Course Remark'
    class Meta:
        proxy = True


class SupplementaryFee(ServiceFee):
    SERVICE = 'Supplementary'
    class Meta:
        proxy = True


class Invoice(SarisModel):
    NUMBER_LENGTH = 6
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    invoice_number = models.CharField(max_length=255, default=reference_number, editable=False, unique=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.DO_NOTHING, editable=False)
    academic_semester = models.ForeignKey(AcademicSemester, on_delete=models.DO_NOTHING)
    service = models.ForeignKey(Service, on_delete=models.DO_NOTHING)
    invoice_amount = models.DecimalField(decimal_places=2, max_digits=20)
    invoice_date = models.DateField()
    currency = models.CharField(max_length=255, choices=Currency.choices, default=Currency.MWK)
    status = models.CharField(max_length=255, choices=InvoiceStatus.choices)
    
    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'invoices'
        ordering = ['-created_at']

    @property
    def paid_amount(self):
        result = self.get_payments().aggregate(total_sum=models.Sum('amount'))
        total_payment = result['total_sum'] if result['total_sum'] is not None else 0
        return total_payment
    
    @property
    def balance(self):
        try:
            total_amount = self.invoice_amount
            total_payment = self.paid_amount
            return float(total_amount - total_payment)
        except:
            pass

    def set_paid(self):
        self.status = InvoiceStatus.PAID

    def set_partial(self):
        self.status = InvoiceStatus.PARTIAL

    def is_pending(self):
        if self.status == InvoiceStatus.PENDING:
            return True
        else:
            return False
        
    def is_paid(self):
        if self.status == InvoiceStatus.PAID:
            return True
        else:
            return False

    def is_partial(self):
        if self.status == InvoiceStatus.PARTIAL:
            return True
        else:
            return False

    def is_not_paid(self):
        return not self.is_paid() 

    def get_payments(self):
        from .models import Transaction
        return Transaction.objects.filter(reference=self.pk)
    
    def has_full_payment(self):
        total_amount = self.paid_amount
        if total_amount >= self.invoice_amount:
            return True
        else:
            return False

    def has_partial_payment(self):
        total_amount = self.paid_amount
        if total_amount < self.invoice_amount:
            return True
        else:
            return False

    def is_for_tuition(self):
        return str(self.service.name).lower() == TuitionFee.SERVICE.lower()

    def change_payment_status(self):
        try:
            if self.has_full_payment():
                self.set_paid()
                self.save()
            if self.has_partial_payment():
                self.set_partial()
                self.save()
        except:
            pass

    def __str__(self) -> str:
        return self.invoice_number
      
    @staticmethod
    def get_by_invoice_number(invoice_number):
        invoice = Invoice.objects.filter(invoice_number=invoice_number).first()
        if not invoice:
            raise InvoiceNotFoundException
        return invoice

          
class Transaction(SarisModel):
    NUMBER_LENGTH = 8
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    reference = models.CharField(max_length=255, default=reference_number)
    trans_date = models.DateField()
    trans_type = models.CharField(max_length=255, choices=TransactionType.choices)
    trans_mode = models.CharField(max_length=255, choices=TransactionMode.choices)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    currency = models.CharField(max_length=255, choices=Currency.choices, default=Currency.MWK)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'transactions'
        ordering = ['created_at']

    @property
    def student_number(self):
        return self.student.student_number
    
    def is_credit(self):
        return self.trans_type==TransactionType.CREDIT
    
    def is_debit(self):
        return self.trans_type==TransactionType.DEBIT

    def credit_description(self):
        self.description = "DEPOSIT"

    def debit_decription(self):
        self.description = "PAYMENT"
    
 
