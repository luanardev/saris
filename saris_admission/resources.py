from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from account.services import UserAccount
from .models import Enrollment, Student, Program, AcademicYear, Campus


class EnrollmentResource(resources.ModelResource):
    id = fields.Field(attribute='id', readonly=True)
    serial_number = fields.Field(attribute='serial_number', column_name='SERIAL_NUMBER')
    initial_semester = fields.Field(attribute='initial_semester', column_name='SEMESTER')
    student = fields.Field(attribute='student', column_name='EMAIL_ADDRESS', widget=ForeignKeyWidget(Student, field='email_address'))
    program = fields.Field(attribute='program', column_name='PROGRAM_CODE',widget=ForeignKeyWidget(Program, field='code'))
    academic_year = fields.Field(attribute='academic_year', column_name='ACADEMIC_YEAR',widget=ForeignKeyWidget(AcademicYear, field='code'))
    intake_type = fields.Field(attribute='intake_type', column_name='INTAKE_TYPE')
    campus = fields.Field(attribute='campus', column_name='CAMPUS_CODE',widget=ForeignKeyWidget(Campus, field='code'))

    class Meta:
        model = Enrollment
        import_id_fields = ['serial_number']
        fields = ['id', 'student', 'program', 'academic_year', 'intake_type', 'campus', 'initial_semester',]

    def before_import_row(self, row, **kwargs):
        first_name = row['FIRST_NAME']
        last_name = row['LAST_NAME']
        gender = row['GENDER']
        email_address = row['EMAIL_ADDRESS']
        phone_number = row['PHONE_NUMBER']

        user_account = UserAccount(first_name, last_name, email_address)
        user = user_account.create_student()

        student, created = Student.objects.get_or_create(
            user=user,
            first_name=first_name, 
            last_name=last_name, 
            gender=gender,
            email_address=email_address,
            phone_number=phone_number,     
        )
        if created:
            student.set_student_number()
            student.set_default_passcode()
            student.save()

            user.set_username(student.student_number)
            user.set_password(student.passcode)
            user.save()
