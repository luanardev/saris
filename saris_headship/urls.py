from django.urls import path
from .apps import SarisHeadshipConfig
from .views import *

app_name = SarisHeadshipConfig.namespace

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    path('lecturercourse/create', CreateLecturerCourseView.as_view(), name='lecturercourse.create'),
    path('lecturercourse/browse', LecturerCourseListView.as_view(), name='lecturercourse.browse'),
    path('lecturercourse/delete', DeleteLecturerCourseView.as_view(), name='lecturercourse.delete'),
    path('lecturercourse/import', ImportLecturerCourseView.as_view(), name='lecturercourse.import'),
    path('lecturercourse/excel',  LecturerCourseExcelTemplateView.as_view(), name='lecturercourse.excel'),
    path('grades/missing',        MissingGradesListView.as_view(), name='grades.missing'),
    path('grades/submit', 	      SubmitGradeView.as_view(), name='grades.submit'),

    path('supplementary',         SupplementrayListView.as_view(), name='supplementary'),
    path('supplementary/submit',  SubmitSupplementaryGradeView.as_view(), name='supplementary.submit'),

    path('courseremark/browse', CourseRemarkListView.as_view(), name='courseremark.browse'),
    path('gradecorrection/browse', GradeCorrectionListView.as_view(), name='gradecorrection.browse'),
    path('courseappeal/<uuid:pk>', CourseAppealDetailsView.as_view(), name='courseappeal.details'),
]
