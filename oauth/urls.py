from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='oauth.login'),
    path('logout', views.logout, name='oauth.logout'),
    path('authorize', views.authorize, name='oauth.authorize'),
]
