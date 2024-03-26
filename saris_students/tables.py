
import django_tables2 as tables
from .models import Student


class StudentTable(tables.Table):

    student_number = tables.Column(
        verbose_name="ID",
        accessor="student_number",
        linkify=("students:student.profile", [tables.A("pk")] )
    )
     
    first_name = tables.Column(
        verbose_name="FIRST NAME",
        accessor="first_name",
        linkify=("students:student.profile", [tables.A("pk")] )
    )

    last_name = tables.Column(
        verbose_name=" LAST NAME",
        accessor="last_name",
        linkify=("students:student.profile", [tables.A("pk")] )
    )

    gender = tables.Column(
        verbose_name="GENDER",
        accessor="gender",
    )
     
    date_of_birth = tables.Column(
        verbose_name="DOB",
        accessor="date_of_birth",
    )
     
    email_address = tables.Column(
        verbose_name="EMAIL",
        accessor="email_address",
    )

    phone_number = tables.Column(
        verbose_name="PHONE",
        accessor="phone_number",
    )

    class Meta:
        model = Student
        fields = ['student_number', 'first_name', 'last_name', 'gender', 'date_of_birth', 'email_address', 'phone_number']
        
