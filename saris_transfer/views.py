
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.views.generic import TemplateView, FormView, DeleteView, DetailView
from django_tables2 import SingleTableView
from django_tables2.views import SingleTableMixin
from django_tables2.paginators import LazyPaginator
from django_filters.views import FilterView
from saris.utils import get_template_name, show_error, show_success
from account.mixins import StaffRequiredMixin
from .filters import TransferFilter
from .forms import ChangeCampusForm, ChangeProgramForm
from .models import Approval, Transfer
from .services import CampusTransfer, ProgramTransfer, RequestApproval, RequestApprover
from .tables import ApprovalHistoryTable, PendingApprovalTable, TransferTable
from .apps import SarisTransferConfig

APP_NAME = SarisTransferConfig.name
REDIRECT_URL = "transfer:home"


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = get_template_name('index.html', APP_NAME)


class ChangeCampusView(StaffRequiredMixin, FormView):
    template_name = get_template_name('request/create.html', APP_NAME)
    form_class = ChangeCampusForm

    def form_valid(self, form):
        try:
            student_number = form.cleaned_data["student_number"]
            campus = form.cleaned_data["campus"]

            transfer = CampusTransfer(student_number, campus)
            transfer.check_transfer()
            transfer.process()
            messages.success(self.request, "Transfer Request successful")
            return redirect(reverse("transfer:request.browse"))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
    

class ChangeProgramView(StaffRequiredMixin, FormView):
    template_name = get_template_name('request/create.html', APP_NAME)
    form_class = ChangeProgramForm

    def form_valid(self, form):
        try:
            student_number = form.cleaned_data["student_number"]
            program = form.cleaned_data["program"]

            transfer = ProgramTransfer(student_number, program)
            transfer.check_transfer()
            transfer.process()
            messages.success(self.request, "Transfer Request successful")
            return redirect(reverse("transfer:request.browse"))
        except Exception as message:
            return show_error(
                request=self.request,
                message=message,
                redirect_url=REDIRECT_URL,
                app_name=APP_NAME
            )
    

class TransfersListView(StaffRequiredMixin, SingleTableMixin, FilterView):
    template_name = get_template_name('request/browse.html', APP_NAME)
    model = Transfer
    table_class = TransferTable
    filterset_class = TransferFilter
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}
    reset_filter_url = 'transfer:request.browse'
    

class TransferDetailsView(StaffRequiredMixin, DetailView):
    template_name = get_template_name('request/details.html', APP_NAME)
    model = Transfer
    context_object_name = 'transfer'


class CancelTransferView(StaffRequiredMixin, DeleteView):
    template_name = get_template_name('request/cancel.html', APP_NAME)
    model = Transfer

    def post(self, request, *args, **kwargs):
        try:
            transfer = self.get_object()
            transfer.delete()
            message = "Transfer Request Cancelled"
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


class ApprovalHistoryListView(StaffRequiredMixin, SingleTableView):
    template_name = get_template_name('approval/history.html', APP_NAME)
    model = Approval
    table_class = ApprovalHistoryTable
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}


    def get_table(self, **kwargs):
        user = self.request.user.staff
        approver = RequestApprover(user)
        history = approver.get_history()
        table = ApprovalHistoryTable(history)
        return table
        
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


class PendingApprovalListView(StaffRequiredMixin, SingleTableView):
    template_name = get_template_name('approval/pending.html', APP_NAME)
    model = Transfer
    table_class = PendingApprovalTable
    paginator_class = LazyPaginator
    table_pagination = {"per_page": 50}


    def get_table(self, **kwargs):
        user = self.request.user.staff
        approver = RequestApprover(user)
        requests = approver.get_requests()
        table = PendingApprovalTable(requests)
        return table
        
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


class ApprovalDetailsView(StaffRequiredMixin, DetailView):
    template_name = get_template_name('approval/details.html', APP_NAME)
    model = Transfer
    context_object_name = 'transfer'


class ApproveRequestView(StaffRequiredMixin, FormView):
    
    def post(self, request, *args, **kwargs):
        try:
            approver = self.request.user.staff
            transfer = request.POST.get("transfer")
            comment = request.POST.get("comment")
            decision = request.POST.get("approval")

            approval = RequestApproval(transfer, approver, decision, comment)
            result = approval.process()

            messages.success(self.request, f"Transfer Request {result}")
            return redirect(reverse("transfer:approval.pending"))
            
        except Exception as message:
            return show_error(
               request=self.request,
               message=message,
               redirect_url=REDIRECT_URL,
               app_name=APP_NAME
            )