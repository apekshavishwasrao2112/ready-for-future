from django.urls import path
from . import views


app_name = 'career'


urlpatterns = [

    # Home page
    path(
        '',
        views.home,
        name='home'
    ),

    # Career profile
    path(
        'profile/',
        views.profile,
        name='profile'
    ),

    # Dashboard
    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

]