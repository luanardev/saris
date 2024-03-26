from account.models import Staff


def get_users_by_department(request):
    department = request.user.staff.department
    return Staff.objects.filter(department=department)