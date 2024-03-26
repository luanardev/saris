from django.urls import path
from .apps import SarisStudentsConfig
from .views import *

app_name = SarisStudentsConfig.namespace

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    path('student', StudentsListView.as_view(), name='browse'),
    path('student/<uuid:pk>', StudentProfileView.as_view(), name='student.profile'),
    path('student/<uuid:pk>/update', UpdateProfileView.as_view(), name='student.update'),
    path('student/kinsman/<uuid:student>/create', CreateKinsmanView.as_view(), name='kinsman.create'),
    path('student/kinsman/<uuid:pk>/update', UpdateKinsmanView.as_view(), name='kinsman.update'),
    path('card', SearchIDCardView.as_view(), name='card'),
    path('card/<uuid:pk>', StudentIDCardView.as_view(), name='card.info'),
    path('card/<uuid:pk>/update', UpdateIDCardView.as_view(), name='card.update'),
    path('card/<uuid:pk>/print', PrintIDCardView.as_view(), name='card.print'),
]
