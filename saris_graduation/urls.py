from django.urls import path
from .apps import SarisGraduationConfig
from .views import *

app_name = SarisGraduationConfig.namespace

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    path('sessions', SessionListView.as_view(), name='session.browse'),
    path('sessions/create', CreateSessionView.as_view(), name='session.create'),
    path('sessions/<uuid:pk>/update', UpdateSessionView.as_view(), name='session.update'),
    path('sessions/<uuid:pk>/delete', DeleteSessionView.as_view(), name='session.delete'),

    path('candidates/process', ProcessCandidatesView.as_view(), name='candidate.process'),
    path('candidates/session', SelectSessionView.as_view(), name='candidate.session'),
    path('candidates/session/<uuid:session>', CandidatesListView.as_view(), name='candidate.browse'),
    path('candidates/<uuid:pk>',CandidateDetailsView.as_view(), name='candidate.details'),
   
    path('booklet', BookletListView.as_view(), name='booklet.browse'),
    path('booklet/create', CreateBookletView.as_view(), name='booklet.create'),
    path('booklet/delete', DeleteBookletView.as_view(), name='booklet.delete'),
    path('booklet/<uuid:pk>/download', DownloadBookletView.as_view(), name='booklet.download'),
]
