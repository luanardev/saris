from django.apps import AppConfig


class SarisAdmissionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'saris_admission'
    namespace = 'admission'
    verbose_name = 'Admission'
