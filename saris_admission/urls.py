from django.urls import path
from .apps import SarisAdmissionConfig
from .views import *

app_name = SarisAdmissionConfig.namespace

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    path('enrollment/create', CreateEnrollmentView.as_view(), name='enrollment.create'),
    path('enrollment/browse', EnrollmentListView.as_view(), name='enrollment.browse'),
    path('enrollment/import', ImportEnrollmentView.as_view(), name='enrollment.import'),
    path('enrollment/<uuid:pk>', EnrollmentDetailsView.as_view(), name='enrollment.details'),
    path('enrollment/<uuid:pk>/update', UpdateEnrollmentView.as_view(), name='enrollment.update'),
    path('enrollment/<uuid:pk>/letter', AdmissionLetterView.as_view(), name='enrollment.letter'),
    path('enrollment/letters', AdmissionLettersView.as_view(), name='enrollment.letters'),
    path('enrollment/excel', ExcelTemplateView.as_view(), name='enrollment.excel'),
    path('withdrawal/create', CreateWithdrawalView.as_view(), name='withdrawal.create'),
    path('withdrawal/browse', WithdrawalListView.as_view(), name='withdrawal.browse'),
    path('withdrawal/<uuid:pk>', WithdrawalDetailsView.as_view(), name='withdrawal.details'),
    path('withdrawal/<uuid:pk>/readmission', ReadmissionView.as_view(), name='withdrawal.readmission'),
]
