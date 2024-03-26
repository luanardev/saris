import django_tables2 as tables
from saris_admission.models import Withdrawal
from saris_assessment.models import CourseAppeal, PublishedGrade, StudentCourse, Supplementary
from saris_billing.models import Invoice
from saris_billing.tables import CustomNumberColumn
from saris_transfer.models import Transfer



class InvoiceTable(tables.Table):
    invoice_number = tables.Column(
        verbose_name="INVOICE NO",
        accessor="invoice_number",
        linkify=("studentportal:invoice", [tables.A("pk")])
    )
    
    service = tables.Column(
        verbose_name="SERVICE",
        accessor="service"
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
    
    invoice_date = tables.DateColumn(
        format="d-M-Y",
        verbose_name="DATE",
        accessor="invoice_date",
    )
    
    class Meta:
        model = Invoice
        fields = [
            'invoice_number','service', 'invoice_amount', 'paid_amount', 'balance', 'academic_semester', 'invoice_date',
        ]


class PaymentTable(InvoiceTable):
    invoice_number = tables.Column(
        verbose_name="INVOICE NO",
        accessor="invoice_number",
        linkify=("studentportal:payment", [tables.A("pk")])
    )


class StudentCourseTable(tables.Table):

    course_code = tables.Column(
        verbose_name="COURSE CODE",
        accessor="course__code",
    )

    course_name = tables.Column(
        verbose_name="COURSE NAME",
        accessor="course__name",
    )

    credit_hours = tables.Column(
        verbose_name="CREDIT HOURS",
        accessor="course__credit_hours",
    )

    course_type = tables.Column(
        verbose_name="COURSE TYPE",
        accessor="course_type",
    )

    course_attempt = tables.Column(
        verbose_name="COURSE ATTEMPT",
        accessor="course_attempt",
    )


    class Meta:
        model = StudentCourse
        fields = ['course_code', 'course_name', 'course_type',
                  'course_attempt', 'credit_hours']


class ExamResultsTable(tables.Table):

    course_code = tables.Column(
        verbose_name="COURSE CODE",
        accessor="course__code",
    )

    course_name = tables.Column(
        verbose_name="COURSE NAME",
        accessor="course__name",
    )

    credit_hours = tables.Column(
        verbose_name="CREDIT HOURS",
        accessor="course__credit_hours",
    )

    course_type = tables.Column(
        verbose_name="COURSE TYPE",
        accessor="course_type",
    )

    course_attempt = tables.Column(
        verbose_name="COURSE ATTEMPT",
        accessor="course_attempt",
    )

    cas_grade = tables.Column(
        verbose_name="CAS GRADE",
        accessor="continous_grade",
    )

    eos_grade = tables.Column(
        verbose_name="EOS GRADE",
        accessor="endsemester_grade",
    )

    final_grade = tables.Column(
        verbose_name="FINAL GRADE",
        accessor="final_grade",
    )

    class Meta:
        model = PublishedGrade
        fields = ['course_code', 'course_name', 'course_type',
                  'course_attempt', 'credit_hours', 'cas_grade', 'eos_grade', 'final_grade']


class TransferTable(tables.Table):

    transfer_type = tables.Column(
        verbose_name="TRANSFER TYPE",
        accessor="transfer_type",
        linkify=("studentportal:transfer_details", [tables.A("pk")] )
    )
     
    academic_semester = tables.Column(
        verbose_name="ACADEMIC SEMESTER",
        accessor="academic_semester",
        linkify=("studentportal:transfer_details", [tables.A("pk")] )
    )

    request_status = tables.Column(
        verbose_name="REQUEST STATUS",
        accessor="request_status",
    )

    request_date = tables.Column(
        verbose_name="REQUEST DATE",
        accessor="request_date",
    )
     
    approval_status = tables.Column(
        verbose_name="APPROVAL STATUS",
        accessor="approval_status",
    )
 
    approval_date = tables.Column(
        verbose_name="APPROVAL DATE",
        accessor="request_date",
    )

    class Meta:
        model = Transfer
        fields = ['transfer_type', 'academic_semester', 'request_status', 'request_date', 'approval_status', 'approval_date']
        

class WithdrawalTable(tables.Table):
    
    withdrawal_type = tables.Column(
        verbose_name="WITHDRAWAL TYPE",
        accessor="withdrawal_type",
        linkify=("studentportal:withdrawal_details", [tables.A("pk")] )
    )

    academic_semester = tables.Column(
        verbose_name="ACADEMIC SEMESTER",
        accessor="academic_semester",
    )

    semester = tables.Column(
        verbose_name="SEMESTER",
        accessor="semester",
    )
    
    period = tables.Column(
        verbose_name="PERIOD",
        accessor="withdrawal_type__period",
    )
    
    status = tables.Column(
        verbose_name="STATUS",
        accessor="status",
    )

    action = tables.LinkColumn(
        viewname="studentportal:withdrawal_details",
        text="View",
        verbose_name="ACTION",
        args=[tables.A("pk")],
        attrs={
            "a": {"class": "btn btn-sm btn-primary"}
        }
    )

    class Meta:
        model = Withdrawal
        fields = [ 'withdrawal_type', 'academic_semester', 'semester', 'period', 'status', 'action']
        

class CourseAppealTable(tables.Table):

    course_code = tables.Column(
        verbose_name="COURSE CODE",
        accessor="course__code",
    )

    course_name = tables.Column(
        verbose_name="COURSE NAME",
        accessor="course__name",
    ) 

    academic_semester = tables.Column(
        verbose_name="ACADEMIC SEMESTER",
        accessor="academic_semester",
    )

    semester = tables.Column(
        verbose_name="SEMESTER",
        accessor="semester",
    )

    appeal_type = tables.Column(
        verbose_name="APPEAL TYPE",
        accessor="appeal_type",
    )

    status = tables.Column(
        verbose_name="STATUS",
        accessor="status",
    )

    action = tables.LinkColumn(
        viewname="studentportal:course_appeal_details",
        text="View",
        verbose_name="ACTION",
        args=[tables.A("pk")],
        attrs={
            "a": {"class": "btn btn-sm btn-primary"}
        }
    )

    class Meta:
        model = CourseAppeal
        fields = ['course_code', 'course_name', 'academic_semester', 'semester', 'appeal_type', 'status', 'action']


class SupplementaryTable(tables.Table):

    course_code = tables.Column(
        verbose_name="COURSE CODE",
        accessor="course__code",
    )

    course_name = tables.Column(
        verbose_name="COURSE NAME",
        accessor="course__name",
    )

    credit_hours = tables.Column(
        verbose_name="CREDIT HOURS",
        accessor="course__credit_hours",
    )

    course_type = tables.Column(
        verbose_name="COURSE TYPE",
        accessor="course_type",
    )

    course_attempt = tables.Column(
        verbose_name="COURSE ATTEMPT",
        accessor="course_attempt",
    )

    status = tables.Column(
        verbose_name="STATUS",
        accessor="status",
    )


    class Meta:
        model = Supplementary
        fields = ['course_code', 'course_name', 'credit_hours', 'course_type', 'course_attempt', 'status' ]

