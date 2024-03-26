
from saris_curriculum.models import StatusType


class BrowseProgramByDepartment:
    
    def get_queryset(self):
        queryset = super().get_queryset()
        department = self.request.user.staff.department
        queryset = queryset.filter(department=department, status=StatusType.ACTIVE)
        return queryset


class BrowseProgramByCampus:
    
    def get_queryset(self):
        queryset = super().get_queryset()
        campus = self.request.user.staff.campus
        queryset = queryset.filter(department__campus=campus, status=StatusType.ACTIVE)
        return queryset


class BrowseCourseByDepartment:
    
    def get_queryset(self):
        queryset = super().get_queryset()
        department = self.request.user.staff.department
        queryset = queryset.filter(department=department, status=StatusType.ACTIVE)
        return queryset


class CurriculumConfigurationFormMixin:

    def get_form_class(self):
        form_class = super().get_form_class()
        department = self.request.user.staff.department
        form_class.base_fields['program'].limit_choices_to = {'department': department}
        form_class.base_fields['academic_semester'].limit_choices_to = {'status': StatusType.ACTIVE}
        return form_class


class MasterCurriculumFormMixin:

    def get_form_class(self):
        form_class = super().get_form_class()
        form_class.base_fields['course'].limit_choices_to = {'status': StatusType.ACTIVE}
        return form_class


class CourseConfigurationFormMixin:

    def get_form_class(self):
        form_class = super().get_form_class()
        form_class.base_fields['course'].limit_choices_to = {'status': StatusType.ACTIVE}
        return form_class


class BrowseCourseByCampus:
    
    def get_queryset(self):
        queryset = super().get_queryset()
        campus = self.request.user.staff.campus
        queryset = queryset.filter(department__campus=campus, status=StatusType.ACTIVE)
        return queryset


class BrowseConfiguredCurriculumByDepartment:
    
    def get_queryset(self):
        queryset = super().get_queryset()
        department = self.request.user.staff.department
        queryset = queryset.filter(program__department=department)
        return queryset
