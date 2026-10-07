from django.urls import path

from . import views


app_name = 'learning'

urlpatterns = [
    path('', views.roadmap, name='roadmap'),
]
