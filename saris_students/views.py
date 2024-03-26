import slugify
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.views.generic import TemplateView, DetailView, FormView, UpdateView
from django_tables2.views import SingleTableMixin
from django_tables2.paginators import LazyPaginator
from django_filters.views import FilterView
from saris.mixins import RenderPDFMixin
from saris.utils import get_template_name, show_error
from account.mixins import StaffRequiredMixin
from .apps import SarisStudentsConfig
from .filters import StudentFilter, StudentSearch
from .forms import IDCardForm, KinsmanForm, StudentForm
from .models import Kinsman, Student
from .services import IDCard
from .tables import StudentTable


APP_NAME = SarisStudentsConfig.name
REDIRECT_URL = "students:home"


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('index.html', APP_NAME)


class StudentsListView(StaffRequiredMixin, SingleTableMixin, FilterView):
    template_name = get_template_name('browse.html', APP_NAME)
    model = Student
    table_class = StudentTable
    filterset_class = StudentFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    reset_filter_url = 'students:browse'


class StudentProfileView(StaffRequiredMixin, DetailView):
    template_name = get_template_name('student/profile.html', APP_NAME)
    model = Student


class UpdateProfileView(StaffRequiredMixin, UpdateView):
    template_name = get_template_name('student/update.html', APP_NAME)
    model = Student
    form_class = StudentForm
    context_object_name = 'student'

    def form_valid(self, form):
        student = form.save()
        messages.success(self.request, "Profile updated")
        return redirect(reverse("students:student.profile", args=[student.pk]))


class CreateKinsmanView(StaffRequiredMixin, FormView):
    template_name = get_template_name('kinsman/create.html', APP_NAME)
    model = Kinsman
    form_class = KinsmanForm
    context_object_name = 'kinsman'

    def get_student(self):
        pk = self.kwargs["student"]
        student = Student.get_by_id(pk)
        return student
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student"] = self.get_student()
        return context
    
    def form_valid(self, form):
        student = self.get_student()
        kinsman = form.save(commit=False)
        kinsman.student = student
        kinsman.save()
        messages.success(self.request, "Kinsman created")
        return redirect(reverse("students:student.profile", args=[student.pk]))


class UpdateKinsmanView(StaffRequiredMixin, UpdateView):
    template_name = get_template_name('kinsman/update.html', APP_NAME)
    model = Kinsman
    form_class = KinsmanForm
    context_object_name = 'kinsman'
    
    def form_valid(self, form):
        kinsman = form.save()
        messages.success(self.request, "Kinsman updated")
        return redirect(reverse("students:student.profile", args=[kinsman.student_id]))


class SearchIDCardView(StaffRequiredMixin, FilterView):
    template_name = get_template_name('card/search.html', APP_NAME)
    model = Student
    filterset_class = StudentSearch
    reset_filter_url = 'students:card'


class StudentIDCardView(StaffRequiredMixin, DetailView):
    template_name = get_template_name('card/info.html', APP_NAME)
    model = Student


class UpdateIDCardView(StaffRequiredMixin, UpdateView):
    template_name = get_template_name('card/update.html', APP_NAME)
    model = Student
    form_class = IDCardForm
    context_object_name = 'student'

    def form_valid(self, form):
        student = form.save()
        messages.success(self.request, "ID Card updated")
        return redirect(reverse("students:card.info", args=[student.pk]))


class PrintIDCardView(StaffRequiredMixin, RenderPDFMixin, TemplateView):
    template_name = get_template_name('card/pdf.html', APP_NAME)
    download_name = "identiy_card"
    
    def get_student(self):
        pk = self.kwargs["pk"]
        student = Student.get_by_id(pk)
        return student

    def get_download_name(self, **kwargs):
        student = self.get_student()
        prefix = student.student_number
        file_name = slugify(f"{prefix}_{self.download_name}")
        return f"{file_name.upper()}.pdf"
    
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = super().get_context_data()
        
        try:
            student = self.get_student()
            context['card'] = IDCard(student)
            return self.render_pdf(request, self.template_name, context)
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
