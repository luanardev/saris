from django.apps import AppConfig


class SarisGraduationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'saris_graduation'
    namespace = 'graduation'
    verbose_name = 'Graduation'

    def ready(self):
        import saris_graduation.signals