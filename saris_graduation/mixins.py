

from saris_graduation.models import Session


class BrowseCandidatesByCampus:
    
    def get_queryset(self):
        queryset = super().get_queryset()
        campus = self.request.user.staff.campus
        queryset = queryset.filter(enrollment__campus=campus)
        return queryset
