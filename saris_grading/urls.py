from django.urls import path
from .apps import SarisGradingConfig
from .views import *

app_name = SarisGradingConfig.namespace

urlpatterns = [
    path('', CourseAllocationView.as_view(), name='home'),
    path('courses', CourseAllocationView.as_view(), name='courses'),
    path('courses/<uuid:pk>', ClassListView.as_view(), name='classlist'),
    path('courses/<uuid:pk>/resultsheet', ResultsheetView.as_view(), name='resultsheet'),
    path('courses/<uuid:pk>/gradeentry', GradeEntryView.as_view(), name='entergrade'),
    path('courses/<uuid:pk>/gradeupload', GradeUploadView.as_view(), name='uploadgrade'),
    path('courses/<uuid:pk>/gradetemplate', GradeTemplateView.as_view(), name='gradetemplate'),
    path('submitgrade', SubmitGradeView.as_view(), name='submitgrade'),
   
]
