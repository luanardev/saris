"""
URL configuration for saris project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static


admin.site.site_title = "SARIS"
admin.site.site_header = "SARIS Administration"
admin.site.index_title = "SARIS Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('oauth/', include('oauth.urls')),

    path('', include('account.urls')),
    path('admission/', include('saris_admission.urls')),
    path('assessment/', include('saris_assessment.urls')), 
    path('billing/', include('saris_billing.urls')),
    path('curriculum/', include('saris_curriculum.urls')), 
    path('grading/', include('saris_grading.urls')), 
    path('graduation/', include('saris_graduation.urls')), 
    path('headship/', include('saris_headship.urls')), 
    path('registration/', include('saris_registration.urls')),
    path('students/', include('saris_students.urls')), 
    path('transfer/', include('saris_transfer.urls')), 
    path('portal/staff/', include('saris_staffportal.urls')),
    path('portal/student/', include('saris_studentportal.urls')), 
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

