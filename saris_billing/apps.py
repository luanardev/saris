from django.apps import AppConfig


class SarisBillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'saris_billing'
    namespace = 'billing'
    verbose_name = 'Billing'
