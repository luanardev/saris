from django.core.files.storage import default_storage
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .tasks import generate_gradebook
from .models import GradeBook


@receiver(post_save, sender=GradeBook)
def create_gradebook(sender, instance, created, **kwargs):
    generate_gradebook.delay(instance.pk)


@receiver(post_delete, sender=GradeBook)
def remove_gradebook(sender, instance, **kwags):
    try:
        path = instance.pdf_file.path
        if path:
            default_storage.delete(path)
    except:
        pass
    