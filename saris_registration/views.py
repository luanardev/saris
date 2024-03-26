from slugify import slugify
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import FormView, TemplateView, DeleteView
from django_tables2 import SingleTableMixin
from django_tables2.views import SingleTableView
from django_tables2.paginators import LazyPaginator
from django_tables2.export import ExportMixin
from django_filters.views import FilterView
from django.contrib import messages
from django.urls import reverse
from saris.tables import BulkSelectionMixin
from saris.utils import get_template_name, show_error, show_success
from account.mixins import StaffRequiredMixin
from saris_registration.mixins import BrowseRegistrationByCampus
from saris_assessment.models import StudentCourse
from .apps import SarisRegistrationConfig
from .models import Registration
from .tables import RegistrationTable, StudentCourseTable
from .filters import RegistrationFilter
from .services import DeregisterCourseListManager, RegisterCourseManager, RegistrationManager, DeregistrationManager
from .forms import RegisterForm, StudentCourseForm


APP_NAME = SarisRegistrationConfig.name
REDIRECT_URL = "registration:home"


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('index.html', APP_NAME)


class RegisterView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('register.html', APP_NAME)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = RegisterForm(request=self.request)
        return context
  
    def post(self, request, *args, **kwargs):
        try:
            student_number = request.POST.get("student_number")
            academic_semester = request.POST.get("academic_semester")
            
            manager = RegistrationManager(student_number, academic_semester)
            register = manager.get_register()
            register.check_duplicate()
            
            invoice_manager = register.get_invoice_manager()

            context = {
                "register" : register,
                "invoice_manager": invoice_manager
            }

            self.request.session["student_number"] = student_number
            self.request.session["academic_semester"] = academic_semester
            self.request.session.save()
            
            template = get_template_name("invoice.html", APP_NAME)
            return render(self.request, template, context)
        except Exception as message:
            return show_error(
                request=self.request, 
                message=message, 
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
 
          
class RegistrationCheckoutView(StaffRequiredMixin, FormView):
    
    def post(self, request, *args, **kwargs):
        try:
            student_number = request.session.get("student_number")
            academic_semester = request.session.get("academic_semester")
            
            manager = RegistrationManager(student_number, academic_semester)
            register = manager.get_register()
            registration = register.process()

            messages.success(self.request, "Student registration successful")
            
            request.session.delete("student_number")
            request.session.delete("academic_semester")
            
            return redirect(reverse("registration:details", args=[registration.pk]))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class DeregisterView(StaffRequiredMixin, DeleteView):
    template_name = get_template_name('deregister.html', APP_NAME)
    model = Registration

    def post(self, request, *args, **kwargs):
        try:
            registration = self.get_object()
            manager = DeregistrationManager(registration)
            manager.process()
            message = "Student deregistration successful"
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


class RegistrationListView(StaffRequiredMixin, SingleTableMixin, BrowseRegistrationByCampus, ExportMixin, FilterView):
    template_name = get_template_name('browse.html', APP_NAME)
    model = Registration
    table_class = RegistrationTable
    filterset_class = RegistrationFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    export_formats = ['xlsx']
    export_name = 'registration_export'
    reset_filter_url = 'registration:browse'
    
    def get_export_filename(self, export_format):
        prefix = self.request.user.staff.campus
        file_name = slugify(f"{prefix}_{self.export_name}")
        return f"{file_name.upper()}.{export_format}"


class RegistrationDetailsView(StaffRequiredMixin, BulkSelectionMixin, SingleTableView):
    template_name = get_template_name('details.html', APP_NAME)
    model = StudentCourse
    table_class = StudentCourseTable
    delete_selected_url = 'registration:course.delete'
    
    def get_registration(self, **kwargs):
        pk = self.kwargs['pk']
        registration = Registration.objects.get(id=pk)
        return registration
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = self.get_registration(**kwargs)
        student_form = StudentCourseForm(registration=registration)
        context["registration"] = registration 
        context["form"] = student_form 
        return context
    
    def get_queryset(self, **kwargs):
        registration = self.get_registration(**kwargs)
        queryset = super().get_queryset()
        queryset = queryset.filter(
            enrollment=registration.enrollment,
            academic_semester=registration.academic_semester,
            semester=registration.semester
        )
        return queryset
    
    def post(self, request, *args, **kwargs):
        try:
            registration = request.POST.get('registration')
            master_course = request.POST.get('course')
            course_attempt = request.POST.get('course_attempt')
            
            manager = RegisterCourseManager(registration, master_course, course_attempt) 
            manager.process() 
            messages.success(request, "Course Registration Successful")
            return redirect(reverse("registration:details", args=[registration]))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        
        
class DeleteStudentCourseView(StaffRequiredMixin, DeleteView):
    model = StudentCourse

    def is_ajax(self, request):
        return request.headers.get('x-requested-with') == 'XMLHttpRequest'

    def post(self, request, *args, **kwargs):

        if self.is_ajax(request):
            try:
                selection = request.POST.get('selection')
                if not selection:
                    return False
                
                student_courses = selection.split(',')
                manager = DeregisterCourseListManager(student_courses)
                manager.process()
                response = {'message': 'Student Course Deleted'}
                return JsonResponse(response)
            except Exception as error:
                response = {'error': str(error)}
                return JsonResponse(response, status=400)
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)
