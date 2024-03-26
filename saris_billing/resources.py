import datetime
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from saris_students.models import Student
from .models import Transaction, TransactionMode, TransactionType

class TransactionResource(resources.ModelResource):
    id = fields.Field(attribute='id', readonly=True)
    amount = fields.Field(attribute='amount', column_name='AMOUNT')
    currency = fields.Field(attribute='currency', column_name='CURRENCY')
    description = fields.Field(attribute='description', column_name='DESCRIPTION')
    student = fields.Field(attribute='student', column_name='STUDENT_NUMBER', widget=ForeignKeyWidget(Student, field='student_number'))
    
    class Meta:
        model = Transaction
        import_id_fields = ['reference', 'student', 'trans_date']
        fields = ['reference', 'trans_date', 'trans_mode', 'description', 'student', 'amount', 'currency']

    def before_save_instance(self, instance, using_transactions, dry_run):
        trans_type = TransactionType.CREDIT
        trans_mode = TransactionMode.ELECTRONIC
        
        
        instance.trans_type = trans_type

        if not instance.trans_mode:
           instance.trans_mode = trans_mode
        
        if not instance.student:
            raise Exception('Transaction has no student')
        
        if not instance.trans_date:
            instance.trans_date = datetime.date.today()

        if not instance.reference:
            instance.set_reference()
    
        if not instance.description:
            instance.description = "DEPOSIT"
            
        return super().before_save_instance(instance, using_transactions, dry_run)

