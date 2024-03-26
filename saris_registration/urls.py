from django.urls import path
from .apps import SarisRegistrationConfig
from .views import *

app_name = SarisRegistrationConfig.namespace

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    path('register', RegisterView.as_view(), name='register'),
    path('checkout', RegistrationCheckoutView.as_view(), name='checkout'),
    path('browse', RegistrationListView.as_view(), name='browse'),
    path('<uuid:pk>', RegistrationDetailsView.as_view(), name='details'),
    path('course/delete', DeleteStudentCourseView.as_view(), name='course.delete'),
    path('<uuid:pk>/deregister', DeregisterView.as_view(), name='deregister')
]