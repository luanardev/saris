class BrowseEnrollmentByCampus:
    
    def get_queryset(self):
        queryset = super().get_queryset()
        campus = self.request.user.staff.campus
        queryset = queryset.filter(campus=campus)
        return queryset


class BrowseEnrollmentByDepartment:

    def get_queryset(self):
        queryset = super().get_queryset()
        department = self.request.user.staff.department
        queryset = queryset.filter(program__department=department)
        return queryset
    

class BrowseWithdrawalByCampus:
    
    def get_queryset(self):
        queryset = super().get_queryset()
        campus = self.request.user.staff.campus
        queryset = queryset.filter(enrollment__campus=campus)
        return queryset