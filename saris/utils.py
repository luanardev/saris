import os
import datetime
import mimetypes
import random
import string
from random import randint
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.core.validators import MaxValueValidator
from django.conf import settings
from django.shortcuts import render


def get_task_feedback():
    return "You will be notified when completed."


def get_template_name(template_path, app_name=None):
    if app_name is None:
        return template_path
    else:
        return f"{app_name}/{template_path}"


def random_number(length):
    return str(randint(0, 10**length-1)).zfill(length)


def random_string(length):
    # Get all the ASCII letters in lowercase and uppercase
    letters = string.ascii_uppercase
    # Randomly choose characters from letters for the given length of the string
    random_string = ''.join(random.choice(letters) for i in range(length))
    return random_string


def reference_number():
    # Convert number to string
    timestamp =  timezone.now()
    str_time = timestamp.strftime("%y%m%d%H%M%S")
    
    # Split the string in half
    half_length = len(str_time) // 2
    first_half = str_time[:half_length]
    second_half = str_time[half_length:]
    
    # Generate random string of size 4
    r_string = random_string(6)
    
    result = f"{first_half}{r_string}{second_half}"

    reference_list = list(result)
    
    # Shuffle the list of characters randomly
    random.shuffle(reference_list)
    
    # Convert the shuffled list back to a string
    shuffled_reference = ''.join(reference_list)
    
    return shuffled_reference
    

def current_year():
    return datetime.date.today().year


def next_year():
    return datetime.date.today().year+1


def previous_year():
    return datetime.date.today().year-1


def current_month():
    return datetime.date.today().month


def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


def year_choices(min_value = None):
    if not min_value:
        min_value = 1920
    return [(r, r) for r in range(min_value, datetime.date.today().year+1)]


def get_file_path(file_name, app_name=None):
    if app_name is None:
        return file_name
    else:
        return f"{app_name}/{file_name}"
    

def download(path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as fh:
            content = fh.read()
            response = HttpResponse(content, content_type=mime_type)
            response['Content-Disposition'] = 'inline; filename=' + file_name
            return response
    raise Http404


def show_feedback(request, message, title=None, redirect_url=None, success=True, app_name=None):
    if not app_name:
        template = "feedback.html"
    else:
        template = get_template_name("feedback.html", app_name)
    context = {
        'message': str(message),
        'success': success,
        'title': title,
        'redirect_url': redirect_url
    }
    return render(request, template, context)


def show_success(request, message, redirect_url=None, app_name=None):
    title = "Successful!"
    return show_feedback(request=request, message=message, title=title, redirect_url=redirect_url, app_name=app_name)


def show_error(request, message, redirect_url=None, app_name=None):
    title = "Oops! there's a problem"
    return show_feedback(request=request, message=message, title=title, redirect_url=redirect_url, success=False, app_name=app_name)


def add_years(start_date, years):
    try:
        return start_date.replace(year=start_date.year + years)
    except ValueError:
        # 👇️ preserve calendar day (if Feb 29th doesn't exist, set to 28th)
        return start_date.replace(year=start_date.year + years, day=28)
