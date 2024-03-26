from django.urls import path
from .apps import SarisCurriculumConfig
from .views import *

app_name = SarisCurriculumConfig.namespace

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    
    path('program/index', ProgramIndexView.as_view(), name='program.index'),
    path('program/create', CreateProgramView.as_view(), name='program.create'),
    path('program/browse', ProgramListView.as_view(), name='program.browse'),
    path('program/<uuid:pk>', ProgramDetailsView.as_view(), name='program.details'),
    path('program/<uuid:pk>/update', UpdateProgramView.as_view(), name='program.update'),
    path('program/import', ImportProgramView.as_view(), name='program.import'),
    path('program/excel', ProgramExcelTemplateView.as_view(), name='program.excel'),
    
    path('course/index', CourseIndexView.as_view(), name='course.index'),
    path('course/create', CreateCourseView.as_view(), name='course.create'),
    path('course/browse', CourseListView.as_view(), name='course.browse'),
    path('course/<uuid:pk>', CourseDetailsView.as_view(), name='course.details'),
    path('course/<uuid:pk>/update', UpdateCourseView.as_view(), name='course.update'),
    path('course/import', ImportCourseView.as_view(), name='course.import'),
    path('course/excel', CourseExcelTemplateView.as_view(), name='course.excel'),
    
    path('mastercurriculum/<uuid:program>/create', CreateMasterCurriculumView.as_view(), name='curriculum.create'),
    path('mastercurriculum/<uuid:pk>/update', UpdateMasterCurriculumView.as_view(), name='curriculum.update'),
    path('mastercurriculum/<uuid:pk>/delete', DeleteMasterCurriculumView.as_view(), name='curriculum.delete'),
    path('mastercurriculum/import', ImportMasterCurriculumView.as_view(), name='curriculum.import'),
    path('mastercurriculum/excel', MasterCurriculumExcelTemplateView.as_view(), name='curriculum.excel'),
    
    path('configuration/index', ConfigurationIndexView.as_view(),name='configuration.index'),
    path('configuration/browse', ConfiguredCurriculumListView.as_view(),name='configuration.browse'),
    path('configuration/create', ConfigureCurriculumView.as_view(), name='configuration.create'),
    path('configuration/<uuid:pk>', ConfiguredCurriculumDetailsView.as_view(), name='configuration.details'),
    path('configuration/<uuid:pk>/delete', DeleteConfiguredCurriculumView.as_view(), name='configuration.delete'),
    path('configuration/<uuid:curriculum>/addcourse', CreateConfiguredCourseView.as_view(), name='configuration.addcourse'),
    path('configuration/<uuid:pk>/deletecourse', DeleteConfiguredCourseView.as_view(), name='configuration.deletecourse'),
    
]
