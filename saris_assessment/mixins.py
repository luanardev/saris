
from saris_assessment.models import AppealStatus, SUPStatus


class BrowseGradeBookByCampus:
    def get_queryset(self):
        queryset = super().get_queryset()
        campus = self.request.user.staff.campus
        queryset = queryset.filter(faculty__campus=campus)
        return queryset
    

class BrowseCourseAppealByCampus:
    def get_queryset(self):
        queryset = super().get_queryset()
        campus = self.request.user.staff.campus
        queryset = queryset.filter(
            enrollment__campus=campus,
            status__in=[AppealStatus.PENDING, AppealStatus.GRADED]
        )
        return queryset
    



class BrowseSupplementaryByDepartment:

    def get_queryset(self):
        queryset = super().get_queryset()
        department = self.request.user.staff.department
        queryset = queryset.filter(
            course__department=department,
            status__in=[SUPStatus.PENDING]
        )
        return queryset
    