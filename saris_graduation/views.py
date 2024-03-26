from django.http import JsonResponse
from slugify import slugify
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.views.generic import TemplateView, DetailView, FormView, UpdateView, DeleteView
from django_tables2.views import SingleTableMixin, SingleTableView
from django_tables2.paginators import LazyPaginator
from django_tables2.export import ExportMixin
from django_filters.views import FilterView
from account.mixins import StaffRequiredMixin
from saris.tables import BulkSelectionMixin
from saris.utils import download, get_task_feedback, get_template_name, show_error, show_success
from saris_graduation.services import BookletManager, CandidatesManager
from saris_graduation.tasks import process_candidates
from .models import Booklet, Candidate, Session
from .apps import SarisGraduationConfig
from .mixins import BrowseCandidatesByCampus
from .filters import CandidateFilter, BookletFilter
from .forms import SessionForm, GraduationForm
from .tables import CandidateTable, SessionTable, BookletTable


APP_NAME = SarisGraduationConfig.name
REDIRECT_URL = "graduation:home"


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('index.html', APP_NAME)


class CreateSessionView(StaffRequiredMixin, FormView):
    template_name = get_template_name('session/create.html', APP_NAME)
    form_class = SessionForm
    model = Session

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Graduation session created")
        return redirect(reverse("graduation:session.browse"))


class UpdateSessionView(StaffRequiredMixin, UpdateView):
    template_name = get_template_name('session/update.html', APP_NAME)
    form_class = SessionForm
    model = Session
    context_object_name = 'session'

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Graduation session updated")
        return redirect(reverse("graduation:session.browse"))
    

class DeleteSessionView(StaffRequiredMixin, DeleteView):
    template_name = get_template_name('session/delete.html', APP_NAME)
    model = Session

    def post(self, request, *args, **kwargs):
        object = self.get_object()
        object.delete()
        messages.success(request, "Graduation session deleted")
        return redirect(reverse("graduation:session.browse")) 


class SessionListView(StaffRequiredMixin, SingleTableView):
    template_name = get_template_name('session/browse.html', APP_NAME)
    model = Session
    table_class = SessionTable
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}


class ProcessCandidatesView(StaffRequiredMixin, FormView):
    template_name = get_template_name('candidate/process.html', APP_NAME)
    form_class = GraduationForm

    def post(self, request, *args, **kwargs):
        try:
            session = request.POST.get("session")
            campus = self.request.user.staff.campus.pk

            manager = CandidatesManager(session, campus)
            manager.check_candidates()

            process_candidates.delay(session, campus)
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


class SelectSessionView(StaffRequiredMixin, FormView):
    template_name = get_template_name('candidate/session.html', APP_NAME)
    form_class = GraduationForm
    
    def form_valid(self, form):
        session = form.cleaned_data['session']
        return redirect(reverse("graduation:candidate.browse", args=[session.pk]))
    

class CandidatesListView(StaffRequiredMixin, SingleTableMixin, BrowseCandidatesByCampus, ExportMixin,  FilterView):
    template_name = get_template_name('candidate/browse.html', APP_NAME)
    model = Candidate
    table_class = CandidateTable
    filterset_class = CandidateFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    export_formats = ['xlsx']
    export_name = 'graduation_list_export'

    
    def get_session(self, **kwargs):
        pk = self.kwargs['session']
        return Session.get_by_id(pk)
    
    def get_context_data(self, **kwargs):
        session = self.get_session(**kwargs)
        context = super().get_context_data(**kwargs)
        context["session"] = session
        return context

    def get_queryset(self, **kwargs):
        session = self.get_session(**kwargs)
        queryset = super().get_queryset()
        queryset = queryset.filter(session=session)
        return queryset
    
    def get_export_filename(self, export_format):
        prefix = self.request.user.staff.campus
        file_name = slugify(f"{prefix}_{self.export_name}")
        return f"{file_name.upper()}.{export_format}"


class CandidateDetailsView(StaffRequiredMixin, DetailView):
    template_name = get_template_name('candidate/details.html', APP_NAME)
    model = Candidate
    context_object_name = 'candidate'


class CreateBookletView(StaffRequiredMixin, FormView):
    template_name = get_template_name('booklet/create.html', APP_NAME)
    form_class = GraduationForm

    
    def post(self, request, *args, **kwargs):
        
        try:
            session = request.POST.get("session")
            booklet = BookletManager(session)
            booklet.check_graduands()
            booklet.create()

            message = get_task_feedback()
            redirect_to = "graduation:booklet.browse"
            return show_success(
                request=self.request,
                message=message,
                redirect_url=redirect_to,
                app_name=APP_NAME
            )
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )


class BookletListView(StaffRequiredMixin, SingleTableMixin, BulkSelectionMixin, FilterView):
    template_name = get_template_name('booklet/browse.html', APP_NAME)
    model = Booklet
    table_class = BookletTable
    filterset_class = BookletFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    reset_filter_url = 'graduation:booklet.browse'
    delete_selected_url = 'graduation:booklet.delete'
   

class DownloadBookletView(StaffRequiredMixin, DetailView):
    model = Booklet

    def get(self, request, *args,  **kwargs):
        booklet = self.get_object()
        if booklet.is_ready():
            file_name = booklet.pdf_file.path
            return download(file_name)
        else:
            message = "Booklet is processing."
            REDIRECT_URL = "graduation:booklet.browse"
            return show_success(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
        

class DeleteBookletView(StaffRequiredMixin, DeleteView):
    model = Booklet

    def is_ajax(self, request):
        return request.headers.get('x-requested-with') == 'XMLHttpRequest'

    def post(self, request, *args, **kwargs):

        if self.is_ajax(request):
            try:
                selection = request.POST.get('selection')
                if not selection:
                    return False
                
                booklets = selection.split(',')
                Booklet.objects.filter(id__in=booklets).delete()
                response = {'message': 'Graduation Booklet Deleted'}
                return JsonResponse(response)
            except Exception as error:
                response = {'error': str(error)}
                return JsonResponse(response, status=400)
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)
