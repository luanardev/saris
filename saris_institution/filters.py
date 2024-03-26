from saris_institution.models import Campus, Faculty


def get_campuses_by_user(request):
    campus = request.user.staff.campus
    return Campus.filter(pk=campus.pk)

def get_faculties_by_campus(request):
    campus = request.user.staff.campus
    return Faculty.filter(campus=campus)