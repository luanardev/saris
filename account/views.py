
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from saris.utils import get_template_name
from .apps import AccountConfig
from .forms import LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm


APP_NAME = AccountConfig.name

STAFF_ACCOUNT_HOME = "home"
STUDENT_ACCOUNT_HOME = "studentportal:home"


class IndexView(TemplateView):
    template_name = get_template_name('index.html', APP_NAME)


class AccountView(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_staff:
            return redirect(reverse(STAFF_ACCOUNT_HOME))
        if user.is_student:
            return redirect(reverse(STUDENT_ACCOUNT_HOME))
        

class LoginView(auth_views.LoginView):
    template_name = get_template_name('login.html', APP_NAME)
    form_class = LoginForm
    redirect_authenticated_user = True
    success_url = 'account'


class LogoutView(auth_views.LogoutView):
    def post(self, request, *args, **kwargs) :
        logout(request)
        return redirect("login")


class PasswordResetView(auth_views.PasswordResetView):
    template_name = get_template_name('forgot_password.html', APP_NAME)
    form_class = UserPasswordResetForm


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = get_template_name('password_change_done.html', APP_NAME)


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = get_template_name('recover_password.html', APP_NAME)
    form_class = UserSetPasswordForm


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = get_template_name('password_reset_done.html', APP_NAME)


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = get_template_name('password_reset_complete.html', APP_NAME)


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = get_template_name('password_change.html', APP_NAME)
    form_class = UserPasswordChangeForm

