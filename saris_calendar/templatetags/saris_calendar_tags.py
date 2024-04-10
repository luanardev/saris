from django import template
from account.models import User
from saris_calendar.models import AcademicSemester 

register = template.Library() 


@register.simple_tag
def academic_semester(user: User):
    try:
        campus = None
        if user.is_staff:
            campus = user.staff.campus
        elif user.is_student:
            campus = user.student.campus
        academic_semester = AcademicSemester.get_active(campus)
        return academic_semester
    except:
        pass
