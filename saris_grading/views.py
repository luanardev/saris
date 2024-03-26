
from typing import Any
from django.http.response import HttpResponse as HttpResponse
import tablib
from slugify import slugify
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpRequest, JsonResponse
from django.views.generic import TemplateView, FormView, DetailView 
from django_tables2 import SingleTableMixin
from django_tables2.paginators import LazyPaginator
from django_tables2.export import ExportMixin
from django_filters.views import FilterView
from account.mixins import StaffMixin, StaffRequiredMixin
from saris.utils import get_template_name, show_error
from saris_assessment.models import StudentCourse, LecturerCourse
from saris_assessment.services import GradeImport, GradeEntry, SingleClass, CourseRegistration
from .apps import SarisGradingConfig
from .mixins import CourseAllocationMixin
from .tables import ClassListTable, ResultsheetTable, GradeTemplateTable
from .filters import ClassListFilter
from .forms import ImportForm

APP_NAME = SarisGradingConfig.name
REDIRECT_URL = "grading:home"


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('index.html', APP_NAME)
 
  
class CourseAllocationView(StaffRequiredMixin, StaffMixin, TemplateView):
    template_name = get_template_name('courses.html', APP_NAME)
    
    def get_context_data(self, **kwargs):
        lecturer = self.get_staff()
        context = super().get_context_data(**kwargs)
        manager = CourseRegistration(lecturer)
        context["manager"] = manager
        return context
    
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
 

class ClassListView(StaffRequiredMixin, SingleTableMixin, CourseAllocationMixin, ExportMixin, FilterView):
    template_name = get_template_name('classlist.html', APP_NAME)
    model = StudentCourse
    table_class = ClassListTable
    filterset_class = ClassListFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    export_formats = ['xlsx']
    export_name = 'class_list_export'
    
    def get_export_filename(self, export_format):
        lecturer_course = self.get_lecturer_course(**self.kwargs)
        manager = SingleClass(lecturer_course)
        academic_semester = manager.academic_semester
        course = manager.course
        file_name = slugify(f"{academic_semester}_{course.code}_{self.export_name}")
        return f"{file_name.upper()}.{export_format}"
     
    def get_queryset(self, **kwargs):
        lecturer_course = self.get_lecturer_course(**kwargs)
        manager = SingleClass(lecturer_course)
        queryset = manager.get_class()
        return queryset


class ResultsheetView(StaffRequiredMixin, SingleTableMixin, CourseAllocationMixin, ExportMixin, FilterView):
    template_name = get_template_name('resultsheet.html', APP_NAME)
    model = StudentCourse
    table_class = ResultsheetTable
    filterset_class = ClassListFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    export_formats = ['xlsx']
    export_name = 'resultsheet_export'

    def get_export_filename(self, export_format):
        lecturer_course = self.get_lecturer_course(**self.kwargs)
        manager = SingleClass(lecturer_course)
        academic_semester = manager.academic_semester
        course = manager.course
        file_name = slugify(f"{academic_semester}_{course.code}_{self.export_name}")
        return f"{file_name.upper()}.{export_format}"

    def get_queryset(self, **kwargs):
        lecturer_course = self.get_lecturer_course(**kwargs)
        manager = SingleClass(lecturer_course)
        queryset = manager.get_class()
        return queryset
  
 
class GradeEntryView(StaffRequiredMixin, CourseAllocationMixin, DetailView):
    template_name = get_template_name('gradeentry.html', APP_NAME)
    model = LecturerCourse
  
    
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


class GradeTemplateView(StaffRequiredMixin, SingleTableMixin, CourseAllocationMixin, ExportMixin, TemplateView):
    model = StudentCourse
    table_class = GradeTemplateTable
    export_name = 'grade_entry'
    export_format = 'xlsx'
    
    def get_export_filename(self, export_format):
        lecturer_course = self.get_lecturer_course(**self.kwargs)
        manager = SingleClass(lecturer_course)
        academic_semester = manager.academic_semester
        course = manager.course
        file_name = slugify(f"{academic_semester}_{course.code}_{self.export_name}")
        return f"{file_name.upper()}.{export_format}"
    
    def get_queryset(self, **kwargs):
        lecturer_course = self.get_lecturer_course(**kwargs)
        manager = SingleClass(lecturer_course)
        queryset = manager.get_class()
        return queryset
    
    def get(self, request, *args,  **kwargs):
        return self.create_export(self.export_format)
    

class GradeUploadView(StaffRequiredMixin, CourseAllocationMixin, FormView):
    template_name = get_template_name('gradeupload.html', APP_NAME)
    form_class = ImportForm

    def form_valid(self, form):
        try: 
            file = form.cleaned_data["file"]
            dataset = tablib.Dataset().load(file)
            
            lecturer_course = self.get_lecturer_course()
            manager = GradeImport(lecturer_course)
            manager.import_data(dataset)
            
            messages.success(self.request, "Operation successful")
            return redirect(reverse("grading:resultsheet", args=[lecturer_course.pk]))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
