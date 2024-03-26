
from saris_assessment.models import AppealStatus, AppealType, SUPStatus


class CourseAllocationFormMixin:

    def get_form_class(self):
        form_class = super().get_form_class()
        department = self.request.user.staff.department
        form_class.base_fields['course'].limit_choices_to = {'department': department}
        form_class.base_fields['lecturer'].limit_choices_to = {'department': department}
        return form_class


class BrowseAllocationByDepartment:

    def get_queryset(self):
        queryset = super().get_queryset()
        department = self.request.user.staff.department
        queryset = queryset.filter(
            course__department=department, 
            lecturer__department=department
        )
        return queryset


class BrowseCourseAppealByDepartment:

    def get_queryset(self):
        queryset = super().get_queryset()
        department = self.request.user.staff.faculty
        queryset = queryset.filter(
            course__department__faculty=department,
            status__in=[AppealStatus.PENDING, AppealStatus.GRADED]
        )
        return queryset


class BrowseCourseRemarkByDepartment:

    def get_queryset(self):
        queryset = super().get_queryset()
        department = self.request.user.staff.department
        queryset = queryset.filter(
            course__department=department,
            appeal_type=AppealType.COURSE_REMARK,
            status__in=[AppealStatus.PENDING, AppealStatus.GRADED]
        )
        return queryset
    

class BrowseGradeCorrectionByDepartment:

    def get_queryset(self):
        queryset = super().get_queryset()
        department = self.request.user.staff.department
        queryset = queryset.filter(
            course__department=department,
            appeal_type=AppealType.GRADE_CORRECTION,
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
    