from django.db import models
from dirtyfields import DirtyFieldsMixin


class SarisModel(DirtyFieldsMixin, models.Model):
    """
    An abstract base class model that provides self-updating
    ``created_at`` and ``updated_at`` fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.get(pk=id)
    
    @classmethod
    def get_all(cls):
        return cls.objects.all()
    
    @classmethod
    def filter(cls, *args, **kwargs):
        return cls.objects.filter(*args, **kwargs)



class WorkStatus(models.TextChoices):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    ERROR = "ERROR"


class WorkMixin:

    def set_pending(self):
        self.status = WorkStatus.PENDING
    
    def set_processing(self):
        self.status = WorkStatus.PROCESSING

    def set_ready(self):
        self.status = WorkStatus.READY

    def set_error(self, error):
        self.error = error
        self.status = WorkStatus.ERROR

    def is_pending(self):
        if self.status == WorkStatus.PENDING:
            return True
        else:
            return False
        
    def is_processing(self):
        if self.status == WorkStatus.PROCESSING:
            return True
        else:
            return False
        
    def is_ready(self):
        if self.status == WorkStatus.READY:
            return True
        else:
            return False
        
    def is_error(self):
        if self.status == WorkStatus.ERROR:
            return True
        else:
            return False
