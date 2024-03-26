from abc import ABC, abstractmethod
from account.models import Staff
from saris_admission.models import Enrollment
from saris_calendar.models import AcademicSemester
from saris_curriculum.models import Program
from saris_institution.models import Campus
from .models import Approval, Approver, Stage, Transfer, TransferStatus, TransferType
from .exceptions import RequestExistsException, PermissionDeniedException


class TransferRequest(ABC):

    def __init__(self, student_number) -> None:
        super().__init__()
        self.student_number = student_number
        self.enrollment = Enrollment.get_active(student_number)
        self.campus = self.enrollment.campus
        self.program = self.enrollment.program
        self.academic_semester = AcademicSemester.get_active(self.campus)
        self.first_stage = Stage.first_stage()

    def _check_request_exists(self):
        transfers = Transfer.objects.filter(
            enrollment=self.enrollment, 
            transfer_type=self.transfer_type,
            request_status=TransferStatus.PENDING,
            approval_status=TransferStatus.PENDING
        ).count()
        if transfers > 0:
            raise RequestExistsException 

    def check_transfer(self):
        self._check_request_exists()
        self.enrollment.check_withdrawal()
        self.enrollment.check_completion()

    @abstractmethod
    def process(self):
        pass
 
        

class CampusTransfer(TransferRequest):

    def __init__(self, student_number, new_campus, summary=None) -> None:
        super().__init__(student_number)
        if isinstance(new_campus, Campus):
            self.new_campus = new_campus
        else:
            self.new_campus = Campus.get_by_id(new_campus)

        self.transfer_type = TransferType.CAMPUS
        self.summary = summary
    
    def _get_summary(self):
        transfer_type = str(self.transfer_type).capitalize()
        campus = str(self.campus).capitalize()
        new_campus = str(self.new_campus).capitalize()
        if self.summary is None:
            return f"{transfer_type} Transfer from {campus} to {new_campus}"
        else:
            return self.summary

    def process(self):
        transfer = Transfer()
        transfer.enrollment = self.enrollment
        transfer.academic_semester = self.academic_semester
        transfer.transfer_type = self.transfer_type
        transfer.stage = self.first_stage
        transfer.new_campus = self.new_campus
        transfer.request_summary = self._get_summary()
        transfer.save()

    
class ProgramTransfer(TransferRequest):

    def __init__(self, student_number, new_program, summary=None) -> None:
        super().__init__(student_number)
        if isinstance(new_program, Program):
            self.new_program = new_program
        else:
            self.new_program = Program.get_by_id(new_program)

        self.transfer_type = TransferType.PROGRAM
        self.summary = summary
    
    def _get_summary(self):
        transfer_type = str(self.transfer_type).capitalize()
        program = str(self.program).capitalize()
        new_program = str(self.new_program).capitalize()
        if self.summary is None:
            return f"{transfer_type} Transfer from {program} to {new_program}"
        else:
            return self.summary

    def process(self):
        transfer = Transfer()
        transfer.enrollment = self.enrollment
        transfer.academic_semester = self.academic_semester
        transfer.transfer_type = self.transfer_type
        transfer.stage = self.first_stage
        transfer.new_program = self.new_program
        transfer.new_campus = self.new_program.department.faculty.campus
        transfer.request_summary = self._get_summary()
        transfer.save()


class RequestApprover(object):

    def __init__(self, staff) -> None:
        if isinstance(staff, Staff):
            self.staff = staff
        else:
            self.staff = Staff.objects.get(pk=staff)
        self.campus = staff.campus

    def _get_approver(self):
        user_group = self.staff.user.groups.all()
        approver = Approver.objects.filter(group__in=user_group).first()
        return approver
    
    def get_requests(self):
        approver = self._get_approver()
        if not approver:
            raise PermissionDeniedException
        
        return Transfer.objects.filter(
            request_status = TransferStatus.PENDING,
            approval_status = TransferStatus.PENDING,
            stage = approver.stage,
            enrollment__campus = self.campus
        )
    
    def get_history(self):
        approver = self._get_approver()
        if not approver:
            raise PermissionDeniedException
        
        return Approval.objects.filter(
            stage = approver.stage,
        )

    
class RequestApproval(RequestApprover):

    def __init__(self, transfer, approver, decision, comment):
        super().__init__(approver)
        if isinstance(transfer, Transfer):
            self.transfer = transfer
        else:
            self.transfer = Transfer.objects.get(pk=transfer)
        self.decision = decision
        self.comment = comment
    
    def _get_decision(self):
        if str(self.decision).lower() == "approved":
            return TransferStatus.APPROVED
        if str(self.decision).lower() == "rejected":
            return TransferStatus.REJECTED
        
    def _create_approval(self):
        approval = Approval()
        approval.transfer = self.transfer
        approval.stage = self.transfer.stage
        approval.approver = self.staff.user
        approval.comment = self.comment
        approval.decision = self._get_decision()
        approval.save()
        return approval

    def _get_next_stage(self):
        current_level = self.transfer.stage.level
        return Stage.objects.filter(level__gt=current_level).first()

    def _update_enrollment(self):
        enrollment = self.transfer.enrollment
        if self.transfer.is_campus_transfer():
            new_campus = self.transfer.new_campus
            enrollment.campus = new_campus
            enrollment.save()
        elif self.transfer.is_program_transfer():
            new_program = self.transfer.new_program
            new_campus = self.transfer.new_campus
            enrollment.program = new_program
            enrollment.campus = new_campus
            enrollment.save()

    def _approve_student(self):
        transfer = self.transfer
        if transfer.is_last_stage():
            transfer.approve()
            transfer.complete()
            transfer.save()
            self._update_enrollment()
        else:
            next_stage = self._get_next_stage()
            transfer.stage = next_stage
            transfer.save()

    def _reject_student(self):
        transfer = self.transfer
        transfer.reject()
        transfer.complete()
        transfer.save()

    def process(self):
        approval = self._create_approval()
        if approval.is_approved():
            self._approve_student()
        elif approval.is_rejected():
            self._reject_student()
        return approval

        
