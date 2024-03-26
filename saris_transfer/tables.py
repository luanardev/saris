
import django_tables2 as tables

from saris.tables import SelectAllCheckBoxColumn
from .models import Approval, Transfer


class TransferTable(tables.Table):
    selection = SelectAllCheckBoxColumn(accessor="pk", orderable=False)
   
    student_number = tables.Column(
        verbose_name="ID",
        accessor="enrollment__student__student_number",
        linkify=("transfer:request.details", [tables.A("pk")] )
    )
     
    student = tables.Column(
        verbose_name="STUDENT",
        accessor="enrollment__student",
        linkify=("transfer:request.details", [tables.A("pk")] )
    )

    academic_semester = tables.Column(
        verbose_name="ACADEMIC SEMESTER",
        accessor="academic_semester",
    )

    transfer_type = tables.Column(
        verbose_name="TRANSFER TYPE",
        accessor="transfer_type",
    )
     
    status = tables.Column(
        verbose_name="STATUS",
        accessor="request_status",
    )
     
    approval = tables.Column(
        verbose_name="APPROVAL",
        accessor="approval_status",
    )

    date = tables.Column(
        verbose_name="DATE",
        accessor="request_date",
    )

    class Meta:
        model = Transfer
        fields = ['student_number', 'student', 'academic_semester', 'transfer_type', 'status', 'approval', 'date']
        exclude = ['selection']
        

class PendingApprovalTable(tables.Table):
  
    student_number = tables.Column(
        verbose_name="ID",
        accessor="enrollment__student__student_number",
        linkify=("transfer:approval.details", [tables.A("pk")] )
    )
     
    student = tables.Column(
        verbose_name="STUDENT",
        accessor="enrollment__student",
        linkify=("transfer:approval.details", [tables.A("pk")] )
    )

    academic_semester = tables.Column(
        verbose_name="ACADEMIC SEMESTER",
        accessor="academic_semester",
    )

    transfer_type = tables.Column(
        verbose_name="TRANSFER TYPE",
        accessor="transfer_type",
    )
     
    stage = tables.Column(
        verbose_name="STAGE",
        accessor="stage",
    )

    date = tables.Column(
        verbose_name="DATE",
        accessor="request_date",
    )
    
    class Meta:
        model = Transfer
        fields = ['student_number', 'student', 'academic_semester', 'transfer_type', 'stage', 'date']
        exclude = ['selection']


class ApprovalHistoryTable(tables.Table):
  
    student_number = tables.Column(
        verbose_name="ID",
        accessor="transfer__enrollment__student__student_number",
    )
     
    student = tables.Column(
        verbose_name="STUDENT",
        accessor="transfer__enrollment__student",
    )

    academic_semester = tables.Column(
        verbose_name="ACADEMIC SEMESTER",
        accessor="transfer__academic_semester",
    )

    transfer_type = tables.Column(
        verbose_name="TRANSFER TYPE",
        accessor="transfer__transfer_type",
    )
     
    stage = tables.Column(
        verbose_name="STAGE",
        accessor="stage",
    )

    approval = tables.Column(
        verbose_name="APPROVAL",
        accessor="decision",
    )

    date = tables.Column(
        verbose_name="DATE",
        accessor="approval_date",
    )
    
    class Meta:
        model = Approval
        fields = ['student_number', 'student', 'academic_semester', 'transfer_type', 'stage', 'approval', 'date']
        exclude = ['selection']

