from slugify import slugify
from django.http import JsonResponse
from django_tables2 import LazyPaginator, SingleTableMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView, DetailView, FormView, DeleteView
from django_renderpdf.views import PDFView
from django_filters.views import FilterView
from saris.tables import BulkSelectionMixin
from saris.utils import download, get_task_feedback, get_template_name, show_error, show_success
from saris_admission.filters import EnrollmentSearch
from saris_admission.models import Enrollment
from account.mixins import StaffMixin, StaffRequiredMixin
from .apps import SarisAssessmentConfig
from .forms import CampusGradeProcessingForm, GradeBookForm, GradeProcessingForm
from .filters import CourseAppealFilter, GradeBookFilter, SupplementaryFilter
from .models import AssessmentVersion, CourseAppeal, GradeBook, SemesterResult, Supplementary
from .mixins import BrowseCourseAppealByCampus, BrowseGradeBookByCampus, BrowseSupplementaryByDepartment
from .tables import CourseAppealTable, GradeBookTable, SupplementaryTable
from .services import AcademicTranscript, GradeBookManager, ResultPublisher, ResultStatement
from .tasks import (
    process_grades, 
    process_appeal_grades, 
    process_missing_grades, 
    process_supplementary_grades, 
    publish_grades, 
    publish_appeal_grades, 
    publish_supplementary_grades
)


APP_NAME = SarisAssessmentConfig.name
REDIRECT_URL = "assessment:home"


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('index.html', APP_NAME)


class SearchResultStatementView(StaffRequiredMixin, FilterView):
    template_name = get_template_name('results/search.html', APP_NAME)
    model = Enrollment
    filterset_class = EnrollmentSearch
    reset_filter_url = 'assessment:results'
    
    
class ResultStatementDetailsView(StaffRequiredMixin, DetailView):
    template_name = get_template_name('results/details.html', APP_NAME)
    model = Enrollment

    def get(self, request, *args, **kwargs):
        try:
            AssessmentVersion.check_active()
            return super().get(request, *args, **kwargs)
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollment = self.get_object()
        context["enrollment"] = enrollment
        context["statement"] = ResultStatement(enrollment)
        return context
    
    
class ProcessResultStatementView(StaffRequiredMixin, DetailView):
    model = Enrollment
    
    def get(self, request, *args, **kwargs):
        try:
            enrollment = self.get_object()
            statement = ResultStatement(enrollment)
            statement.process()
            messages.success(self.request, "Grade processing successful")
            
            return redirect(reverse("assessment:results.details", args=[enrollment.pk]))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        

class DownloadResultStatementView(StaffRequiredMixin, PDFView):
    template_name = get_template_name('results/download.html', APP_NAME)
    download_name = "Result_Statement"
    
    def get_enrollment(self, **kwargs):
        pk = kwargs.pop("pk")
        enrollment = get_object_or_404(Enrollment, pk=pk)
        return enrollment

    def get_download_name(self, **kwargs):
        enrollment = self.get_enrollment(**kwargs)
        prefix = enrollment.student.student_number
        file_name = slugify(f"{prefix}_{self.download_name}")
        return f"{file_name.upper()}.pdf"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollment = self.get_enrollment(**kwargs)
        context["statement"] = ResultStatement(enrollment)
        return context


class PublishSemesterResultView(StaffRequiredMixin, DetailView):
    model = SemesterResult
    
    def get(self, request, *args, **kwargs):
        try:
            semester_result = self.get_object()
            
            publisher = ResultPublisher(semester_result)
            publisher.publish()
            messages.success(self.request, "Grades Publishing Successful")

            return redirect(reverse("assessment:results.details", args=[semester_result.enrollment_id]))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class GradesProcessingView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('grades/index.html', APP_NAME)


class ProcessGradesView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('grades/process.html', APP_NAME)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = GradeProcessingForm(request=self.request)
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            academic_semester = request.POST.get("academic_semester")

            process_grades.delay(academic_semester)

            message = get_task_feedback()
            return show_success(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )

    
class PublishGradesView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('grades/publish.html', APP_NAME)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = GradeProcessingForm(request=self.request)
        return context

    def post(self, request, *args, **kwargs):
        try:
            academic_semester = request.POST.get("academic_semester")

            publish_grades.delay(academic_semester)

            message = get_task_feedback()
            return show_success(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class ProcessMissingGradesView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('grades/process_missing_grades.html', APP_NAME)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = GradeProcessingForm(request=self.request)
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            academic_semester = request.POST.get("academic_semester")

            process_missing_grades.delay(academic_semester)

            message = get_task_feedback()
            return show_success(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class AppealListView(StaffRequiredMixin, SingleTableMixin, BrowseCourseAppealByCampus, FilterView):
    template_name = get_template_name('appeals/browse.html', APP_NAME)
    model = CourseAppeal
    table_class = CourseAppealTable
    filterset_class = CourseAppealFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    reset_filter_url = 'assessment:appeals'
    

class AppealDetailsView(StaffRequiredMixin, DetailView):
    template_name = get_template_name('appeals/details.html', APP_NAME)
    model = CourseAppeal
    context_object_name = "courseappeal"


class ProcessAppealGradesView(StaffRequiredMixin, StaffMixin, TemplateView):
    template_name = get_template_name('appeals/process.html', APP_NAME)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CampusGradeProcessingForm(request=self.request)
        return context   
 
    def post(self, request, *args, **kwargs):
        try:
            campus = request.POST.get('campus')
            
            process_appeal_grades.delay(campus)

            message = get_task_feedback()
            return show_success(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class PublishAppealGradesView(StaffRequiredMixin, StaffMixin, TemplateView):
    template_name = get_template_name('appeals/publish.html', APP_NAME)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CampusGradeProcessingForm(request=self.request)
        return context

    def post(self, request, *args, **kwargs):
        try:
            campus = request.POST.get('campus') or self.get_campus()
            
            publish_appeal_grades.delay(campus)

            message = get_task_feedback()
            return show_success(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class SupplementaryListView(StaffRequiredMixin, SingleTableMixin, BrowseSupplementaryByDepartment, FilterView):
    template_name = get_template_name('supplementary/browse.html', APP_NAME)
    model = Supplementary
    table_class = SupplementaryTable
    filterset_class = SupplementaryFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    reset_filter_url = 'assessment:supplementary'
    

class SupplementaryDetailsView(StaffRequiredMixin, DetailView):
    template_name = get_template_name('supplementary/details.html', APP_NAME)
    model = Supplementary
    context_object_name = "supplementary"


class ProcessSupplementaryGradesView(StaffRequiredMixin, StaffMixin, TemplateView):
    template_name = get_template_name('supplementary/process.html', APP_NAME)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CampusGradeProcessingForm(request=self.request)
        return context   
 
    def post(self, request, *args, **kwargs):
        try:
            campus = request.POST.get('campus')
            
            process_supplementary_grades.delay(campus)

            message = get_task_feedback()
            return show_success(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class PublishSupplementaryGradesView(StaffRequiredMixin, StaffMixin, TemplateView):
    template_name = get_template_name('supplementary/publish.html', APP_NAME)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CampusGradeProcessingForm(request=self.request)
        return context

    def post(self, request, *args, **kwargs):
        try:
            campus = request.POST.get('campus') or self.get_campus()
            
            publish_supplementary_grades.delay(campus)

            message = get_task_feedback()
            return show_success(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class SearchTranscriptView(StaffRequiredMixin, FilterView):
    template_name = get_template_name('transcript/search.html', APP_NAME)
    model = Enrollment
    filterset_class = EnrollmentSearch
    reset_filter_url = 'assessment:transcript'


class DownloadTranscriptView(StaffRequiredMixin, PDFView):
    template_name = get_template_name('transcript/download.html', APP_NAME)
    filename = "Academic_Transcript"

    def get_enrollment(self, **kwargs):
        pk = kwargs.pop("pk")
        enrollment = get_object_or_404(Enrollment, pk=pk)
        return enrollment

    def get_download_name(self, **kwargs):
        enrollment = self.get_enrollment(**kwargs)
        prefix = enrollment.student.student_number
        file_name = slugify(f"{prefix}_{self.download_name}")
        return f"{file_name.upper()}.pdf"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollment = self.get_enrollment(**kwargs)
        context["transcript"] = AcademicTranscript(enrollment)
        return context


class CreateGradeBookView(StaffRequiredMixin, FormView):
    template_name = get_template_name('gradebook/create.html', APP_NAME)


    def get_form(self, **kwargs):
        return GradeBookForm(request=self.request)


    def post(self, request, *args, **kwargs):
        
        try:
            faculty = request.POST.get("faculty")
            academic_semester = request.POST.get("academic_semester")
            gradebook = GradeBookManager(faculty, academic_semester)
            gradebook.create()

            message = get_task_feedback()
            REDIRECT_URL = "assessment:gradebook"
            return show_success(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class GradeBookListView(StaffRequiredMixin, SingleTableMixin, BulkSelectionMixin, BrowseGradeBookByCampus, FilterView):
    template_name = get_template_name('gradebook/browse.html', APP_NAME)
    model = GradeBook
    table_class = GradeBookTable
    filterset_class = GradeBookFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    reset_filter_url = 'assessment:gradebook'
    delete_selected_url = 'assessment:gradebook.delete'
   

class DownloadGradeBookView(StaffRequiredMixin, DetailView):
    model = GradeBook

    def get(self, request, *args,  **kwargs):
        gradebook = self.get_object()
        if gradebook.is_ready():
            file_name = gradebook.pdf_file.path
            return download(file_name)
        else:
            message = "Grade Book is processing."
            REDIRECT_URL = "assessment:gradebook"
            return show_success(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        

class DeleteGradeBookView(StaffRequiredMixin, DeleteView):
    model = GradeBook

    def is_ajax(self, request):
        return request.headers.get('x-requested-with') == 'XMLHttpRequest'

    def post(self, request, *args, **kwargs):

        if self.is_ajax(request):
            try:
                selection = request.POST.get('selection')
                if not selection:
                    return False
                
                gradebooks = selection.split(',')
                GradeBook.objects.filter(id__in=gradebooks).delete()
                response = {'message': 'Grade Book Deleted'}
                return JsonResponse(response)
            except Exception as error:
                response = {'error': str(error)}
                return JsonResponse(response, status=400)
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)
