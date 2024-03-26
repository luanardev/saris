from django.apps import AppConfig


class SarisTransferConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'saris_transfer'
    namespace = 'transfer'
    verbose_name = 'Student Transfer'
