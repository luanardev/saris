from django import template 
from django.conf import settings

from account.models import User
register = template.Library() 

@register.simple_tag 
def profile_picture(user: User):
    if user.profile_picture:
        return f"{settings.BASE_URL}/media/{user.profile_picture}"

@register.simple_tag 
def passport_photo(user: User):
    if user.passport_photo:
        return f"{settings.BASE_URL}/media/{user.passport_photo}"

@register.simple_tag 
def signature(user: User):
    if user.signature:
        return f"{settings.BASE_URL}/media/{user.signature}"