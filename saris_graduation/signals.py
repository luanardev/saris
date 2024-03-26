from django.core.files.storage import default_storage
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .tasks import generate_booklet
from .models import Booklet


@receiver(post_save, sender=Booklet)
def create_booklet(sender, instance, created, **kwargs):
    generate_booklet.delay(instance.pk)


@receiver(post_delete, sender=Booklet)
def remove_booklet(sender, instance, **kwags):
    try:
        path = instance.pdf_file.path
        if path:
            default_storage.delete(path)
    except:
        pass
    