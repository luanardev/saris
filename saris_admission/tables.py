import django_tables2 as tables

from saris.tables import SelectAllCheckBoxColumn
from .models import Enrollment, Withdrawal


class EnrollmentTable(tables.Table):
    selection = SelectAllCheckBoxColumn(accessor="pk", orderable=False)
   
    student_number = tables.Column(
        verbose_name="ID",
        accessor="student__student_number",
        linkify=("admission:enrollment.details", [tables.A("pk")] )
    )
     
    student = tables.Column(
        verbose_name="STUDENT",
        accessor="student",
        linkify=("admission:enrollment.details", [tables.A("pk")] )
    )
    
    program = tables.Column(
        verbose_name="PROGRAM",
        accessor="program",
    )
    
    intake_type = tables.Column(
        verbose_name="INTAKE TYPE",
        accessor="intake_type",
    )
    
    academic_year = tables.Column(
        verbose_name="ACADEMIC YEAR",
        accessor="academic_year",
    )
    
    semester = tables.Column(
        verbose_name="SEMESTER",
        accessor="semester",
    )
    
    campus = tables.Column(
        verbose_name="CAMPUS",
        accessor="campus",
    )
    
    status = tables.Column(
        verbose_name="STATUS",
        accessor="status",
    )


    class Meta:
        model = Enrollment
        fields = ['student_number', 'student', 'program', 'intake_type', 'academic_year', 'semester', 'campus', 'status']
        exclude = ['selection', 'serial_number']
        

class WithdrawalTable(tables.Table):
    selection = tables.CheckBoxColumn(accessor="pk", orderable=False)
   
    student_number = tables.Column(
        verbose_name="ID",
        accessor="enrollment__student__student_number",
        linkify=("admission:withdrawal.details", [tables.A("pk")] )
    )
     
    student = tables.Column(
        verbose_name="STUDENT",
        accessor="enrollment__student",
        linkify=("admission:withdrawal.details", [tables.A("pk")] )
    )

    academic_semester = tables.Column(
        verbose_name="ACADEMIC SEMESTER",
        accessor="academic_semester",
    )

    semester = tables.Column(
        verbose_name="STUDY SEMESTER",
        accessor="semester",
    )
    
    
    withdrawal_type = tables.Column(
        verbose_name="WITHDRAWAL",
        accessor="withdrawal_type",
    )
    
    period = tables.Column(
        verbose_name="PERIOD",
        accessor="withdrawal_type__period",
    )
    
    status = tables.Column(
        verbose_name="STATUS",
        accessor="status",
    )


    class Meta:
        model = Withdrawal
        fields = ['student_number', 'student', 'academic_semester', 'semester', 'withdrawal_type', 'period', 'status']
        exclude = ['selection']
        
