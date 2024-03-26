from django import template 
from django.conf import settings
from saris_institution.models import University
register = template.Library() 

def get_university():
    return University.get_info()

@register.simple_tag
def org_name():
    university = get_university()
    return university.name

@register.simple_tag
def org_acronym():
    university = get_university()
    if university.acronym:
        return university.acronym
    else:
        return university.name

@register.simple_tag
def org_postal_address():
    university = get_university()
    return university.postal_address

@register.simple_tag
def org_email_address():
    university = get_university()
    return university.email_address

@register.simple_tag
def org_telephone_one():
    university = get_university()
    return university.telephone_one

@register.simple_tag
def org_telephone_two():
    university = get_university()
    return university.telephone_two

@register.simple_tag
def org_city():
    university = get_university()
    return university.city

@register.simple_tag
def org_country():
    university = get_university()
    return university.country

@register.simple_tag
def org_favicon():
    university = get_university()
    return f"{settings.BASE_URL}/{university.favicon.url}"

@register.simple_tag
def org_logo():
    university = get_university()
    return f"{settings.BASE_URL}/{university.logo.url}"

@register.simple_tag
def org_website():
    university = get_university()
    return university.website_domain