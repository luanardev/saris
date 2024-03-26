import tablib
from slugify import slugify
from django.shortcuts import redirect, render
from django.views.generic import FormView, TemplateView, UpdateView, DetailView, DeleteView
from django_tables2.views import SingleTableMixin
from django_tables2.paginators import LazyPaginator
from django_tables2.export import ExportMixin
from django_filters.views import FilterView
from django.contrib import messages
from django.urls import reverse
from saris.utils import download, get_template_name, get_file_path, show_error
from account.mixins import StaffRequiredMixin
from .mixins import BrowseConfiguredCurriculumByDepartment, BrowseCourseByDepartment, BrowseProgramByDepartment
from .mixins import CourseConfigurationFormMixin, CurriculumConfigurationFormMixin, MasterCurriculumFormMixin
from .models import  Program, Course, ConfiguredCourse,  MasterCurriculum, ConfiguredCurriculum
from .services import CurriculumConfigurator
from .tables import ConfiguredCourseTable, ProgramTable, CourseTable, MasterCurriculumTable,  ConfiguredCurriculumTable
from .resources import ProgramResource, CourseResource, MasterCurriculumResource
from .forms import CourseForm, ProgramForm, ImportForm, MasterCurriculumForm,  CourseConfigurationForm, CurriculumConfigurationForm
from .filters import ProgramFilter, CourseFilter, MasterCurriculumFilter,ConfiguredCurriculumFilter, ConfiguredCourseFilter
from .apps import SarisCurriculumConfig


APP_NAME = SarisCurriculumConfig.name
REDIRECT_URL = "curriculum:home"


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('index.html', APP_NAME)


class ProgramIndexView(DashboardView):
    template_name = get_template_name('program/index.html', APP_NAME)  


class CourseIndexView(DashboardView):
    template_name = get_template_name('course/index.html', APP_NAME)
  
  
class ConfigurationIndexView(DashboardView):
    template_name = get_template_name('configuration/index.html', APP_NAME)


class CreateProgramView(StaffRequiredMixin, FormView):
    template_name = get_template_name('program/create.html', APP_NAME)
    form_class = ProgramForm
    model = Program

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Program created")
        return redirect(reverse("curriculum:program.create"))


class UpdateProgramView(StaffRequiredMixin, UpdateView):
    template_name = get_template_name('program/update.html', APP_NAME)
    form_class = ProgramForm
    model = Program
    context_object_name = 'program'

    def form_valid(self, form):
        program = form.save()
        messages.success(self.request, "Program updated")
        return redirect(reverse("curriculum:program.details", args=[program.id]))


class ProgramListView(StaffRequiredMixin, SingleTableMixin, BrowseProgramByDepartment, ExportMixin, FilterView):
    template_name = get_template_name('program/browse.html', APP_NAME)
    model = Program
    table_class = ProgramTable
    filterset_class = ProgramFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    export_formats = ['xlsx']
    export_name = 'program_export'
    reset_filter_url = 'curriculum:program.browse'
    
    def get_export_filename(self, export_format):
        prefix = self.request.user.staff.department
        file_name = slugify(f"{prefix}_{self.export_name}")
        return f"{file_name.upper()}.{export_format}"
 
   
class ProgramDetailsView(StaffRequiredMixin, SingleTableMixin, FilterView):
    template_name = get_template_name('program/details.html', APP_NAME)
    model = MasterCurriculum
    table_class = MasterCurriculumTable
    filterset_class = MasterCurriculumFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 10}
    
    def get_program(self, **kwargs):
        pk = self.kwargs['pk']
        program = Program.objects.get(id=pk)
        return program

    def get_context_data(self, **kwargs):
        program = self.get_program(**kwargs)
        context = super().get_context_data(**kwargs)
        context["program"] = program
        return context

    def get_queryset(self, **kwargs):
        program = self.get_program(**kwargs)
        queryset = super().get_queryset()
        queryset = queryset.filter(program=program)
        return queryset


class CreateMasterCurriculumView(StaffRequiredMixin, MasterCurriculumFormMixin, FormView):
    template_name = get_template_name('curriculum/create.html', APP_NAME)
    form_class = MasterCurriculumForm
    model = MasterCurriculum
    
    def get_program(self, **kwargs):
        pk = self.kwargs['program']
        program = Program.objects.get(id=pk)
        return program
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        program = self.get_program()
        form = MasterCurriculumForm(initial={'program': program})
        context["program"] =  program
        context["form"] =  form
        return context
    
    def form_valid(self, form):
        program = self.get_program()
        curriculum = form.save(commit=False)
        curriculum.program = program
        curriculum.save()
        messages.success(self.request, "Program course added")
        return redirect(reverse("curriculum:program.details", args=[program.id]))


class UpdateMasterCurriculumView(StaffRequiredMixin, UpdateView):
    template_name = get_template_name('curriculum/update.html', APP_NAME)
    form_class = MasterCurriculumForm
    model = MasterCurriculum
    context_object_name = 'curriculum'

    def form_valid(self, form):
        curriculum = form.save()
        program = curriculum.program
        messages.success(self.request, "Program course updated")
        return redirect(reverse("curriculum:program.details", args=[program.id]))


class DeleteMasterCurriculumView(StaffRequiredMixin, DeleteView):
    template_name = get_template_name('curriculum/confirm_delete.html', APP_NAME)
    model = MasterCurriculum

    def post(self, request, *args, **kwargs):
        object = self.get_object()
        program = object.program
        object.delete()
        messages.success(request, "Course deleted")
        return redirect(reverse("curriculum:program.details", args=[program.id])) 


class CreateCourseView(StaffRequiredMixin, FormView):
    template_name = get_template_name('course/create.html', APP_NAME)
    form_class = CourseForm
    model = Course

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Course created")
        return redirect(reverse("curriculum:course.create"))    


class UpdateCourseView(StaffRequiredMixin, UpdateView):
    template_name = get_template_name('course/update.html', APP_NAME)
    form_class = CourseForm
    model = Course
    context_object_name = 'course'
    
    def form_valid(self, form):
        course = form.save()
        messages.success(self.request, "Course updated")
        return redirect(reverse("curriculum:course.details", args=[course.id]))


class CourseDetailsView(StaffRequiredMixin, DetailView):
    template_name = get_template_name('course/details.html', APP_NAME)
    model = Course
    context_object_name = 'course'


class CourseListView(StaffRequiredMixin, SingleTableMixin, BrowseCourseByDepartment, ExportMixin, FilterView):
    template_name = get_template_name('course/browse.html', APP_NAME)
    model = Course
    table_class = CourseTable
    filterset_class = CourseFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    export_formats = ['xlsx']
    export_name = 'course_export'
    reset_filter_url = 'curriculum:course.browse'
    
    def get_export_filename(self, export_format):
        prefix = self.request.user.staff.department
        file_name = slugify(f"{prefix}_{self.export_name}")
        return f"{file_name.upper()}.{export_format}"

    
class ImportCourseView(StaffRequiredMixin, FormView):
    template_name = get_template_name('course/import.html', APP_NAME)
    form_class = ImportForm

    def form_valid(self, form):
        file = form.cleaned_data["file"]
        result = None
        try:
            dataset = tablib.Dataset().load(file)
            resource = CourseResource()
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


class ImportProgramView(StaffRequiredMixin, FormView):
    template_name = get_template_name('program/import.html', APP_NAME)
    form_class = ImportForm

    def form_valid(self, form):
        file = form.cleaned_data["file"]
        result = None
        try:
            dataset = tablib.Dataset().load(file)
            resource = ProgramResource()
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


class ImportMasterCurriculumView(StaffRequiredMixin, FormView):
    template_name = get_template_name('curriculum/import.html', APP_NAME)
    form_class = ImportForm

    def form_valid(self, form):
        file = form.cleaned_data["file"]
        result = None
        try:
            dataset = tablib.Dataset().load(file)
            resource = MasterCurriculumResource()
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


class ProgramExcelTemplateView(StaffRequiredMixin, TemplateView):
    file_name = get_file_path('downloads/program.xlsx', APP_NAME)

    def get(self, request, *args,  **kwargs):
        return download(self.file_name)


class CourseExcelTemplateView(StaffRequiredMixin, TemplateView):
    file_name = get_file_path('downloads/course.xlsx', APP_NAME)

    def get(self, request, *args,  **kwargs):
        return download(self.file_name)
 
   
class MasterCurriculumExcelTemplateView(StaffRequiredMixin, TemplateView):
    file_name = get_file_path('downloads/curriculum.xlsx', APP_NAME)

    def get(self, request, *args,  **kwargs):
        return download(self.file_name)


class ConfigureCurriculumView(StaffRequiredMixin, CurriculumConfigurationFormMixin, FormView):
    template_name = get_template_name('configuration/create.html', APP_NAME)
    form_class = CurriculumConfigurationForm
    model = ConfiguredCurriculum

    def form_valid(self, form):
        try:
            program = form.cleaned_data["program"]
            academic_semester = form.cleaned_data["academic_semester"]
            semester = form.cleaned_data["semester"]
            configurator = CurriculumConfigurator(program=program, semester=semester, academic_semester=academic_semester)
            curriculum = configurator.configure()
            messages.success(self.request, "Master Curriculum has been copied")
            return redirect(reverse("curriculum:configuration.details", args=[curriculum.id]))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class DeleteConfiguredCurriculumView(StaffRequiredMixin, DeleteView):
    template_name = get_template_name('configuration/confirm_curriculum_delete.html', APP_NAME)
    model = ConfiguredCurriculum
    context_object_name = 'object'

    def post(self, request, *args, **kwargs):
        object = self.get_object()
        object.delete()
        messages.success(request, "Curriculum deleted")
        return redirect(reverse("curriculum:configuration.browse"))


class ConfiguredCurriculumListView(StaffRequiredMixin, SingleTableMixin, BrowseConfiguredCurriculumByDepartment, ExportMixin, FilterView):
    template_name = get_template_name('configuration/browse.html', APP_NAME)
    model = ConfiguredCurriculum
    table_class = ConfiguredCurriculumTable
    filterset_class = ConfiguredCurriculumFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    export_formats = ['xlsx']
    export_name = 'configured_curriculum_export'
    reset_filter_url = 'curriculum:configuration.browse'
    
    def get_export_filename(self, export_format):
        prefix = self.request.user.staff.department
        file_name = slugify(f"{prefix}_{self.export_name}")
        return f"{file_name.upper()}.{export_format}"
 
   
class ConfiguredCurriculumDetailsView(StaffRequiredMixin, SingleTableMixin, FilterView):
    template_name = get_template_name('configuration/details.html', APP_NAME)
    model = ConfiguredCourse
    table_class = ConfiguredCourseTable
    filterset_class = ConfiguredCourseFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 10}

    def get_configured_curriculum(self, **kwargs):
        pk = self.kwargs['pk']
        curriculum = ConfiguredCurriculum.objects.get(id=pk)
        return curriculum

    def get_context_data(self, **kwargs):
        curriculum = self.get_configured_curriculum(**kwargs)
        context = super().get_context_data(**kwargs)
        context["curriculum"] = curriculum
        return context

    def get_queryset(self, **kwargs):
        curriculum = self.get_configured_curriculum(**kwargs)
        queryset = super().get_queryset()
        queryset = queryset.filter(curriculum=curriculum)
        return queryset


class CreateConfiguredCourseView(StaffRequiredMixin, CourseConfigurationFormMixin, FormView):
    template_name = get_template_name('configuration/addcourse.html', APP_NAME)
    form_class = CourseConfigurationForm
    model = ConfiguredCourse

    def get_configured_curriculum(self, **kwargs):
        pk = self.kwargs['curriculum']
        curriculum = ConfiguredCurriculum.objects.get(id=pk)
        return curriculum

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curriculum = self.get_configured_curriculum()
        form = CourseConfigurationForm(initial={'curriculum': curriculum})
        context["curriculum"] = curriculum
        context["form"] = form
        return context

    def form_valid(self, form):
        curriculum = self.get_configured_curriculum()
        configured = form.save(commit=False)
        configured.curriculum = curriculum
        configured.save()
        messages.success(self.request, "Program course added")
        return redirect(reverse("curriculum:configuration.details", args=[curriculum.id]))


class UpdateConfiguredCourseView(StaffRequiredMixin, UpdateView):
    template_name = get_template_name('configuration/update.html', APP_NAME)
    form_class = CourseConfigurationForm
    model = ConfiguredCourse
    context_object_name = 'object'

    def form_valid(self, form):
        configured = form.save()
        curriculum = configured.curriculum
        messages.success(self.request, "Program course updated")
        return redirect(reverse("curriculum:configuration.details", args=[curriculum.id]))


class DeleteConfiguredCourseView(StaffRequiredMixin, DeleteView):
    template_name = get_template_name('configuration/confirm_course_delete.html', APP_NAME)
    model = ConfiguredCourse
    context_object_name = 'object'

    def post(self, request, *args, **kwargs):
        object = self.get_object()
        curriculum = object.curriculum
        object.delete()
        messages.success(request, "Course deleted")
        return redirect(reverse("curriculum:configuration.details", args=[curriculum.id]))
