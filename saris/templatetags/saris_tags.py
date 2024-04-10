from django import template 
from django.conf import settings

from account.models import User
register = template.Library() 

@register.simple_tag 
def base_url(url):
    return f"{settings.BASE_URL}/{url}"

@register.filter
def capitalize(text):
    return str(text).capitalize()


@register.simple_tag
def user_campus(user: User):
    try:
        if user.is_student:
            return user.student.campus
        
        if user.is_staff:
            return user.staff.campus
    except:
        pass
