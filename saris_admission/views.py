import tablib
from slugify import slugify
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views.generic import TemplateView, FormView, UpdateView, DetailView
from django_tables2.views import SingleTableMixin
from django_tables2.paginators import LazyPaginator
from django_tables2.export import ExportMixin
from django_filters.views import FilterView
from formtools.wizard.views import SessionWizardView
from saris.utils import get_template_name, get_file_path, download, show_error
from saris.mixins import RenderPDFMixin
from account.mixins import StaffRequiredMixin
from .apps import SarisAdmissionConfig
from .models import Enrollment, Withdrawal
from .forms import StudentForm, EnrollmentForm, EnrollmentUpdateForm, ImportForm, WithdrawalForm
from .filters import EnrollmentFilter, EnrollmentSearch, AdmissionLettersFilter, WithdrawalFilter
from .mixins import BrowseEnrollmentByCampus, BrowseWithdrawalByCampus
from .resources import EnrollmentResource
from .services import StudentEnrollment, StudentReadmission, StudentWithdrawal, AdmissionLetters, AdmissionLetter
from .tables import EnrollmentTable, WithdrawalTable

APP_NAME = SarisAdmissionConfig.name
REDIRECT_URL = "admission:home"


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('index.html', APP_NAME)


class CreateEnrollmentView(StaffRequiredMixin, SessionWizardView):
    template_name = get_template_name('enrollment/create.html', APP_NAME)
    form_list = [StudentForm, EnrollmentForm]

    def done(self, form_list, **kwargs):
        student_form = form_list[0]
        enrollment_form = form_list[1]

        student = student_form.save(commit=False)        
        enrollment = enrollment_form.save(commit=False)
        processor = StudentEnrollment(student, enrollment)
        processor.process()

        messages.success(self.request, "Student Enrollment successful")
        return redirect(reverse("admission:enrollment.details", args=[enrollment.pk]))


class UpdateEnrollmentView(StaffRequiredMixin, UpdateView):
    template_name = get_template_name('enrollment/update.html', APP_NAME)
    form_class = EnrollmentUpdateForm
    model = Enrollment
    context_object_name = 'enrollment'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(instance={
            'enrollment': self.object,
            'student': self.object.student,
        })
        return kwargs

    def form_valid(self, form):
        objects = form.save()
        enrollment = objects['enrollment']
        messages.success(self.request, "Enrollment updated")
        return redirect(reverse("admission:enrollment.details", args=[enrollment.pk]))


class EnrollmentDetailsView(StaffRequiredMixin, DetailView):
    template_name = get_template_name('enrollment/details.html', APP_NAME)
    model = Enrollment
    context_object_name = 'enrollment'


class EnrollmentListView(StaffRequiredMixin, SingleTableMixin, BrowseEnrollmentByCampus, ExportMixin, FilterView):
    template_name = get_template_name('enrollment/browse.html', APP_NAME)
    model = Enrollment
    table_class = EnrollmentTable
    filterset_class = EnrollmentFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    export_formats = ['xlsx']
    export_name = 'admission_export'
    reset_filter_url = 'admission:enrollment.browse'
    
    def get_export_filename(self, export_format):
        prefix = self.request.user.staff.campus
        file_name = slugify(f"{prefix}_{self.export_name}")
        return f"{file_name.upper()}.{export_format}"

    
class SearchEnrollmentView(StaffRequiredMixin, FilterView):
    template_name = get_template_name('enrollment/search.html', APP_NAME)
    model = Enrollment
    filterset_class = EnrollmentSearch
    reset_filter_url = 'admission:enrollment.search'


class ImportEnrollmentView(StaffRequiredMixin, FormView):
    template_name = get_template_name('enrollment/import.html', APP_NAME)
    form_class = ImportForm

    def form_valid(self, form):
        file = form.cleaned_data["file"]
        result = None
        try:
            dataset = tablib.Dataset().load(file)
            resource = EnrollmentResource()
            result = resource.import_data(dataset=dataset, raise_errors=True)
            messages.success(self.request, "Operation successful")
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )

        context = super().get_context_data()
        context['form'] = form
        context['result'] = result

        return render(self.request, self.template_name, context)


class AdmissionLetterView(StaffRequiredMixin, RenderPDFMixin, TemplateView):
    template_name = get_template_name('letter/single.html', APP_NAME)
    download_name = "Admission_Letter"
    
    
    def get_enrollment(self, **kwargs):
        pk = kwargs.pop("pk")
        enrollment = get_object_or_404(Enrollment, pk=pk)
        return enrollment

    def get_download_name(self, **kwargs):
        enrollment = self.get_enrollment(**kwargs)
        prefix = enrollment.student.student_number
        file_name = slugify(f"{prefix}_{self.download_name}")
        return f"{file_name.upper()}.pdf"
    
    def get(self, request, *args, **kwargs):
        context = super().get_context_data()
        
        try:
            enrollment = self.get_enrollment(**kwargs)
            context['letter'] = AdmissionLetter(enrollment)
            return self.render_pdf(request, self.template_name, context)
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class AdmissionLettersView(StaffRequiredMixin, BrowseEnrollmentByCampus, RenderPDFMixin, FilterView):
    template_name = get_template_name('letter/filter.html', APP_NAME)
    model = Enrollment
    filterset_class = AdmissionLettersFilter
    reset_filter_url = 'admission:enrollment.letters'

   
    def get(self, request, *args, **kwargs):
        
        if len(request.GET) == 0:
            return super().get(request)
        else:  
            try:
                enrollments = self.get_queryset()
                manager = AdmissionLetters(enrollments)
                letters = manager.get_letters()
                context = {"letters": letters}
                template_name = get_template_name('letter/bulk.html', APP_NAME)
                return self.render_pdf(request, template_name, context)
            except Exception as message:
                return show_error(
                    request=self.request,
                    message=message,
                    redirect_url=REDIRECT_URL,
                    app_name=APP_NAME
                )


class ExcelTemplateView(StaffRequiredMixin, TemplateView):
    file_name = get_file_path('downloads/admission.xlsx', APP_NAME)

    def get(self, request, *args,  **kwargs):
        return download(self.file_name)


class CreateWithdrawalView(StaffRequiredMixin, FormView):
    template_name = get_template_name('withdrawal/create.html', APP_NAME)
    form_class = WithdrawalForm

    def form_valid(self, form):
        try:
            student_number = form.cleaned_data["student_number"]
            withdrawal_type = form.cleaned_data["withdrawal_type"]
            processor = StudentWithdrawal(student_number, withdrawal_type)
            withdrawal = processor.process()
            messages.success(self.request, "Student Withdrawal successful")
            return redirect(reverse("admission:withdrawal.details", args=[withdrawal.pk]))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class WithdrawalListView(StaffRequiredMixin, SingleTableMixin, BrowseWithdrawalByCampus, ExportMixin, FilterView):
    template_name = get_template_name('withdrawal/browse.html', APP_NAME)
    model = Withdrawal
    table_class = WithdrawalTable
    filterset_class = WithdrawalFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    export_formats = ['xlsx']
    export_name = 'withdrawal_export'
    reset_filter_url = 'admission:withdrawal.browse'
    
    def get_export_filename(self, export_format):
        prefix = self.request.user.staff.campus
        file_name = slugify(f"{prefix}_{self.export_name}")
        return f"{file_name.upper()}.{export_format}"


class WithdrawalDetailsView(StaffRequiredMixin, DetailView):
    template_name = get_template_name('withdrawal/details.html', APP_NAME)
    model = Withdrawal
    context_object_name = 'withdrawal'


class ReadmissionView(StaffRequiredMixin, DetailView):
    model = Withdrawal

    def get(self, request, *args, **kwargs):
        try:
            withdrawal = self.get_object()
            readmission = StudentReadmission(withdrawal)
            readmission.process()
            enrollment = readmission.enrollment
            messages.success(self.request, "Student Readmission successful")
            return redirect(reverse("admission:enrollment.details", args=[enrollment.pk]))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )

       
