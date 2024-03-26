from django.urls import path
from .apps import SarisAssessmentConfig
from .views import *

app_name = SarisAssessmentConfig.namespace

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    
    path('results', SearchResultStatementView.as_view(), name='results'),
    path('results/<uuid:pk>', ResultStatementDetailsView.as_view(), name='results.details'),
    path('results/<uuid:pk>/process', ProcessResultStatementView.as_view(), name='results.process'),
    path('results/<uuid:pk>/download', DownloadResultStatementView.as_view(), name='results.download'),
    path('results/<uuid:pk>/publish', PublishSemesterResultView.as_view(), name='results.publish'),
    
    path('transcript',SearchTranscriptView.as_view(), name='transcript'),
    path('transcript/<uuid:pk>/download', DownloadTranscriptView.as_view(), name='transcript.download'),
    
    path('grades', GradesProcessingView.as_view(), name='grades'),
    path('grades/process', ProcessGradesView.as_view(), name='grades.process'),
    path('grades/missing/process', ProcessMissingGradesView.as_view(), name='grades.missing.process'),
    path('grades/publish', PublishGradesView.as_view(), name='grades.publish'),

    path('appeals', AppealListView.as_view(), name='appeals'),
    path('appeals/<uuid:pk>', AppealDetailsView.as_view(), name='appeals.details'),
    path('appeals/process', ProcessAppealGradesView.as_view(), name='appeals.process'),
    path('appeals/publish', PublishAppealGradesView.as_view(), name='appeals.publish'),

    path('supplementary', SupplementaryListView.as_view(), name='supplementary'),
    path('supplementary/<uuid:pk>', SupplementaryDetailsView.as_view(), name='supplementary.details'),
    path('supplementary/process', ProcessSupplementaryGradesView.as_view(), name='supplementary.process'),
    path('supplementary/publish', PublishSupplementaryGradesView.as_view(), name='supplementary.publish'),

    path('gradebook', GradeBookListView.as_view(), name='gradebook'),
    path('gradebook/create', CreateGradeBookView.as_view(), name='gradebook.create'),
    path('gradebook/delete', DeleteGradeBookView.as_view(), name='gradebook.delete'),
    path('gradebook/<uuid:pk>/download', DownloadGradeBookView.as_view(), name='gradebook.download'),
]
