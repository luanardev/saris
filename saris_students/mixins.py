
class BrowseStudentsByCampus:
    
    def get_queryset(self):
        queryset = super().get_queryset()
        campus = self.request.user.staff.campus
        queryset = queryset.filter(campus=campus)
        return queryset