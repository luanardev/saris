from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from account.models import Staff


class StaffRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return HttpResponseRedirect(reverse('login'))  # Redirect to the main login page
        return super().dispatch(request, *args, **kwargs)


class StudentRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_student:
            return HttpResponseRedirect(reverse('login'))  # Redirect to the main login page
        return super().dispatch(request, *args, **kwargs)


class ActivationRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_active:
            return HttpResponseRedirect(reverse('login'))  # Redirect to the main login page
        return super().dispatch(request, *args, **kwargs)
    

class StaffMixin:
    
    def get_staff(self, **kwargs) -> Staff:
        try:
            staff = self.request.user.staff
            return staff
        except:
            raise Exception("User does not have staff record")
    
    def get_campus(self, **kwargs):
        try:
            campus = self.request.user.staff.campus
            return campus
        except:
            raise Exception("User does not have campus")
        
    def get_department(self, **kwargs):
        try:
            department = self.request.user.staff.department
            return department
        except:
            raise Exception("User does not have department")
            