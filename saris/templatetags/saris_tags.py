from django import template 
from django.conf import settings
register = template.Library() 

@register.simple_tag 
def base_url(url):
    return f"{settings.BASE_URL}/{url}"

@register.filter
def capitalize(text):
    return str(text).capitalize()

