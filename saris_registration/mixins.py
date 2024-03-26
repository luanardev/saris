
from saris_calendar.models import AcademicSemester


class BrowseRegistrationByCampus:
    
    def get_campus(self):
        campus = self.request.user.staff.campus
        return campus
    
    def get_academic_semester(self):
        campus = self.get_campus()
        academic_semester = AcademicSemester.get_active(campus)
        if self.request.GET.get("academic_semester"):
            academic_semester  = self.request.GET.get("academic_semester") 
        return academic_semester
    
    def get_queryset(self, **kwargs):
        queryset = super().get_queryset()
        academic_semester = self.get_academic_semester()
        queryset = queryset.filter(academic_semester=academic_semester)
        return queryset
