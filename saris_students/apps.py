from django.apps import AppConfig


class SarisStudentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'saris_students'
    namespace = 'students'
    verbose_name = 'Students'
