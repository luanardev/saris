from django.apps import AppConfig


class SarisCalendarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'saris_calendar'
    namespace = 'calendar'
    verbose_name = 'Calendar'
    
