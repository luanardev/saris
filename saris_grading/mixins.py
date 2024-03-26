from saris_assessment.models import LecturerCourse
from saris_assessment.services import SingleClass


class CourseAllocationMixin:

    def get_lecturer_course(self, **kwargs):
        pk = self.kwargs['pk']
        lecturer_course = LecturerCourse.get_by_id(pk)
        return lecturer_course

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lecturer_course = self.get_lecturer_course(**kwargs)
        single_class = SingleClass(lecturer_course)
        context["manager"] = single_class
        return context
