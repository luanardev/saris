import tablib
from slugify import slugify
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View, ListView, TemplateView, FormView, DeleteView, DetailView
from django_tables2.views import SingleTableMixin
from django_tables2.paginators import LazyPaginator
from django_tables2.export import ExportMixin
from django_filters.views import FilterView
from saris.tables import BulkSelectionMixin
from saris.utils import get_template_name, get_file_path, download, show_error
from account.mixins import StaffMixin, StaffRequiredMixin
from saris_assessment.services import AppealGradeEntry, CourseAllocationManager, MissingGrade, GradeEntry, SUPGradeEntry, SupplementaryGrade
from saris_assessment.models import CourseAppeal, LecturerCourse, StudentCourse, Supplementary
from .apps import SarisHeadshipConfig
from .forms import CourseAllocationForm, AppealGradeForm, ImportForm
from .mixins import BrowseAllocationByDepartment,  BrowseCourseRemarkByDepartment, BrowseGradeCorrectionByDepartment, BrowseSupplementaryByDepartment
from .resources import LecturerCourseResource
from .tables import CourseAllocationTable, CourseAppealTable
from .filters import CourseAllocationFilter, CourseAppealFilter


APP_NAME = SarisHeadshipConfig.name
REDIRECT_URL = "headship:home"


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('index.html', APP_NAME)


class LecturerCourseListView(StaffRequiredMixin, SingleTableMixin, BrowseAllocationByDepartment, BulkSelectionMixin, ExportMixin, FilterView):
    template_name = get_template_name('lecturercourse/browse.html', APP_NAME)
    model = LecturerCourse
    table_class = CourseAllocationTable
    filterset_class = CourseAllocationFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    export_formats = ['xlsx']
    exclude_columns = ['selection']
    export_name = 'course_allocation'
    reset_filter_url = 'headship:lecturercourse.browse'
    delete_selected_url = 'headship:lecturercourse.delete'
    
    def get_export_filename(self, export_format):
        prefix = self.request.user.staff.department
        file_name = slugify(f"{prefix}_{self.export_name}")
        return f"{file_name.upper()}.{export_format}"
    
     
class CreateLecturerCourseView(StaffRequiredMixin, FormView):
    template_name = get_template_name('lecturercourse/create.html', APP_NAME)
    form_class = CourseAllocationForm
    model = LecturerCourse
       
    def get_form(self, **kwargs):
        form = CourseAllocationForm(request=self.request)
        return form

    def post(self, request, *args, **kwargs):
        try:
            lecturer = request.POST.get('lecturer')
            courses = request.POST.getlist("course")
            
            manager = CourseAllocationManager(lecturer, courses)
            manager.process()

            messages.success(self.request, "Course allocation successful")
            return redirect(reverse("headship:lecturercourse.create"))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class DeleteLecturerCourseView(StaffRequiredMixin, DeleteView):
    model = LecturerCourse
    
    def is_ajax(self, request):
        return request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    def post(self, request, *args, **kwargs):
        
        if self.is_ajax(request):
            try:
                selection = request.POST.get('selection')
                if not selection:
                    return False
                id_array = selection.split(',')
                LecturerCourse.objects.filter(id__in=id_array).delete()
                response = {'message': 'successful'}
                return JsonResponse(response)
            except Exception as error:
                response = {'error': str(error)}
                return JsonResponse(response, status=400)
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)
       

class MissingGradesListView(StaffRequiredMixin, ListView):
    template_name = get_template_name('grades/missing.html', APP_NAME)
    model = StudentCourse
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        department = self.request.user.staff.department
        manager = MissingGrade(department)
        context["manager"] = manager
        return context


class SubmitGradeView(StaffRequiredMixin, FormView):
    
    def is_ajax(self, request):
        return request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    def post(self, request, *args, **kwargs):
        
        if self.is_ajax(request):
            student_course = request.POST.get('student_course')
            continous_grade = request.POST.get('continous_grade')
            endsemester_grade = request.POST.get('endsemester_grade')
            try:
                manager = GradeEntry(student_course, continous_grade, endsemester_grade)
                manager.process()
                response = {'message': 'successful'}
                return JsonResponse(response)
            except Exception as error:
                response = {'error': str(error)}
                return JsonResponse(response, status=400)
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)


class ImportLecturerCourseView(StaffRequiredMixin, FormView):
    template_name = get_template_name('lecturercourse/import.html', APP_NAME)
    form_class = ImportForm

    def form_valid(self, form):
        file = form.cleaned_data["file"]
        result = None
        try:
            dataset = tablib.Dataset().load(file)
            resource = LecturerCourseResource()
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


class LecturerCourseExcelTemplateView(StaffRequiredMixin, View):
    file_name = get_file_path('downloads/lecturercourse.xlsx', APP_NAME)

    def get(self, request, *args,  **kwargs):
        return download(self.file_name)


class CourseRemarkListView(StaffRequiredMixin, StaffMixin, SingleTableMixin, BrowseCourseRemarkByDepartment, ExportMixin, FilterView):
    template_name = get_template_name('courseappeal/course_remark.html', APP_NAME)
    model = CourseAppeal
    table_class = CourseAppealTable
    filterset_class = CourseAppealFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    exclude_columns = ["action"]
    export_formats = ['xlsx']
    export_name = 'course_appeal'
    reset_filter_url = 'headship:courseremark.browse'
    
    def get_export_filename(self, export_format):
        prefix = self.get_department()
        file_name = slugify(f"{prefix}_{self.export_name}")
        return f"{file_name.upper()}.{export_format}"
    

class GradeCorrectionListView(StaffRequiredMixin, StaffMixin, SingleTableMixin, BrowseGradeCorrectionByDepartment, ExportMixin, FilterView):
    template_name = get_template_name('courseappeal/grade_correction.html', APP_NAME)
    model = CourseAppeal
    table_class = CourseAppealTable
    filterset_class = CourseAppealFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    exclude_columns = ["action"]
    export_formats = ['xlsx']
    export_name = 'grade_correction'
    reset_filter_url = 'headship:gradecorrection.browse'
    
    def get_export_filename(self, export_format):
        prefix = self.get_department()
        file_name = slugify(f"{prefix}_{self.export_name}")
        return f"{file_name.upper()}.{export_format}"
    

class CourseAppealDetailsView(StaffRequiredMixin, DetailView):
    template_name = get_template_name('courseappeal/details.html', APP_NAME)
    model = CourseAppeal
    context_object_name = "courseappeal"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AppealGradeForm(instance=self.get_object())
        return context
       
    def post(self, request, *args, **kwargs):
        
        try:
            appeal_course = self.get_object()
            continous_grade = request.POST.get('continous_grade')
            endsemester_grade = request.POST.get('endsemester_grade')
            manager = AppealGradeEntry(appeal_course, continous_grade, endsemester_grade)
            manager.process()
            messages.success(self.request, "Grade uploaded")
            return redirect(reverse("headship:courseremark.browse"))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class SupplementrayListView(StaffRequiredMixin, ListView):
    template_name = get_template_name('grades/supplementary.html', APP_NAME)
    model = Supplementary
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        department = self.request.user.staff.department
        manager = SupplementaryGrade(department)
        context["manager"] = manager
        return context
    

class SubmitSupplementaryGradeView(StaffRequiredMixin, FormView):
    
    def is_ajax(self, request):
        return request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    def post(self, request, *args, **kwargs):
        
        if self.is_ajax(request):
            student_course = request.POST.get('student_course')
            endsemester_grade = request.POST.get('endsemester_grade')
            try:
                manager = SUPGradeEntry(student_course, endsemester_grade)
                manager.process()
                response = {'message': 'successful'}
                return JsonResponse(response)
            except Exception as error:
                response = {'error': str(error)}
                return JsonResponse(response, status=400)
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)

