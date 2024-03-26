from .models import AcademicSemester


def get_academic_semester_by_campus(request):
    campus = request.user.staff.campus
    return AcademicSemester.filter(campus=campus)
