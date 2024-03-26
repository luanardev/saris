from django.apps import AppConfig


class SarisAssessmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'saris_assessment'
    namespace = 'assessment'
    verbose_name = 'Assessment'

    def ready(self) -> None:
        import saris_assessment.signals
