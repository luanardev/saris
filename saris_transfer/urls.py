from django.urls import path
from .apps import SarisTransferConfig
from .views import *

app_name = SarisTransferConfig.namespace

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    path('campus', ChangeCampusView.as_view(), name='request.campus'),
    path('program', ChangeProgramView.as_view(), name='request.program'),
    path('request', TransfersListView.as_view(), name='request.browse'),
    path('request/<uuid:pk>', TransferDetailsView.as_view(), name='request.details'),
    path('request/<uuid:pk>/cancel', CancelTransferView.as_view(), name='request.cancel'),

    path('history', ApprovalHistoryListView.as_view(), name='approval.history'),
    path('approval', PendingApprovalListView.as_view(), name='approval.pending'),
    path('approval/<uuid:pk>', ApprovalDetailsView.as_view(), name='approval.details'),
    path('approval/create', ApproveRequestView.as_view(), name='approval.create'),
  
]
