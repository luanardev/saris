from django.apps import AppConfig


class SarisRegistrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'saris_registration'
    namespace = 'registration'
    verbose_name = 'Registration'
