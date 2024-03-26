from django.apps import AppConfig


class SarisGradingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'saris_grading'
    namespace = 'grading'
    verbose_name = 'Grade Entry'
