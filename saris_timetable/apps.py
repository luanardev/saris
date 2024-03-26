from django.apps import AppConfig


class SarisTimetableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'saris_timetable'
    namespace = 'timetable'
    verbose_name = 'Timetable'
