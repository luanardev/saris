import uuid
from datetime import date
from django.db import models
from django.contrib.auth.models import Group
from saris.models import SarisModel
from account.models import User
from saris_admission.models import Enrollment
from saris_calendar.models import AcademicSemester
from saris_curriculum.models import Program
from saris_institution.models import Campus


class TransferStatus(models.TextChoices):
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'


class TransferType(models.TextChoices):
    PROGRAM = 'PROGRAM'
    CAMPUS = 'CAMPUS'


class Stage(SarisModel):
    id = models.BigAutoField(primary_key=True, unique=True)
    level = models.IntegerField()
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Stage'
        verbose_name_plural = 'stages'

    def __str__(self):
        return self.name
    
    @staticmethod
    def first_stage():
        stage = Stage.objects.get(level=1)
        if not stage:
            raise Exception("Approval Stage Not Found")
        return stage
    
    @staticmethod
    def last_stage():
        stage = Stage.objects.order_by("-level").first()
        return stage


class Approver(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    stage = models.ForeignKey(Stage, on_delete=models.DO_NOTHING)
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = 'Approver'
        verbose_name_plural = 'approvers'

    def __str__(self) -> str:
        return self.group.name
    
    
    @staticmethod
    def get_by_stage(stage):
        if not isinstance(stage, Stage):
            stage = Stage.objects.get(id=stage)
        return Stage.objects.filter(stage=stage)
    
    @staticmethod
    def get_by_group(group):
        if not isinstance(group, Group):
            group = Group.objects.get(id=group)
        return Approver.objects.filter(group=group)


class Transfer(SarisModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.DO_NOTHING)
    academic_semester = models.ForeignKey(AcademicSemester, on_delete=models.DO_NOTHING)
    transfer_type = models.CharField(max_length=255, choices=TransferType.choices)
    stage = models.ForeignKey(Stage, on_delete=models.DO_NOTHING, blank=True, null=True)
    new_program = models.ForeignKey(Program, on_delete=models.DO_NOTHING, blank=True, null=True)
    new_campus = models.ForeignKey(Campus, on_delete=models.DO_NOTHING, blank=True, null=True)
    request_status = models.CharField(max_length=255,choices=TransferStatus.choices, default=TransferStatus.PENDING, blank=True, null=True)
    request_date = models.DateField(auto_now=True, blank=True, null=True)
    request_summary = models.TextField(blank=True, null=True)
    approval_status = models.CharField(max_length=255,choices=TransferStatus.choices, default=TransferStatus.PENDING, blank=True, null=True)
    approval_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Transfer'
        verbose_name_plural = 'transfers'

    def __str__(self):
        return f"{self.enrollment}"
    
    def can_cancel(self):
        if self.has_approvals():
            return False
        else:
            return True

    def has_approvals(self):
        approvals = self.approvals()
        return approvals.exists()

    def approve(self):
        self.approval_status = TransferStatus.APPROVED
        self.approval_date = date.today()

    def reject(self):
        self.approval_status = TransferStatus.REJECTED
        self.approval_date = date.today()
        
    def complete(self):
        self.request_status = TransferStatus.COMPLETED
    
    def is_pending(self):
        return self.request_status==TransferStatus.PENDING

    def is_completed(self):
        return self.request_status==TransferStatus.COMPLETED

    def is_approved(self):
        return self.approval_status==TransferStatus.APPROVED

    def is_rejected(self):
        return self.approval_status==TransferStatus.REJECTED
    
    def is_campus_transfer(self):
        return self.transfer_type == TransferType.CAMPUS
    
    def is_program_transfer(self):
        return self.transfer_type == TransferType.PROGRAM

    def is_last_stage(self):
        last_stage = Stage.last_stage()
        if self.stage.pk == last_stage.pk:
            return True
        else:
            return False

    def approvals(self):
        from .models import Approval
        return Approval.objects.filter(transfer=self)


class Approval(SarisModel):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.DO_NOTHING)
    decision = models.CharField(max_length=255, choices=TransferStatus.choices)
    comment = models.CharField(max_length=255, blank=True, null=True)
    approver = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    approval_date = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Approval'
        verbose_name_plural = 'approvals'
        ordering = ['stage']

    def is_approved(self):
        return self.decision==TransferStatus.APPROVED

    def is_rejected(self):
        return self.decision==TransferStatus.REJECTED
    

