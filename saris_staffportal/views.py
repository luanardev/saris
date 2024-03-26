
from django.views.generic import TemplateView
from saris.utils import get_template_name
from account.mixins import StaffMixin, StaffRequiredMixin
from saris_staffportal.apps import SarisStaffportalConfig


APPS = [
    {"name": "Applications", "url": "admission:home","description": "Manage Applications"},
    {"name": "Admission", "url": "admission:home", "description": "Student Admission"},
    {"name": "Registration", "url": "registration:home", "description": "Student Registration"},
    {"name": "Assessment", "url": "assessment:home","description": "Student Assessment"},
    {"name": "Billing", "url": "billing:home", "description": "Student Billing"},
    {"name": "Curriculum", "url": "curriculum:home","description": "Manage Curriculum"},
    {"name": "Transfers", "url": "transfer:home","description": "Manage Transfers"},
    {"name": "Students", "url": "students:home", "description": "Students Directory"},
    {"name": "Headship", "url": "headship:home", "description": "Manage Department"},
    {"name": "Grade Entry", "url": "grading:home", "description": "Upload Student Grades"},
    {"name": "Timetable", "url": "home", "description": "Manage Timetable"},
    {"name": "Graduation", "url": "graduation:home","description": "Manage Graduation"},
]


APP_NAME = SarisStaffportalConfig.name


class Dashboard(StaffRequiredMixin, StaffMixin, TemplateView):
    template_name = get_template_name('index.html', APP_NAME)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["apps"] = APPS
        return context
    

