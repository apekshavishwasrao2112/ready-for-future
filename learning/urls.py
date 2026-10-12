from django.urls import path

from . import views


app_name = 'learning'

urlpatterns = [
    path('', views.roadmap, name='roadmap'),
    path('progress/<slug:task_key>/', views.update_task_progress, name='progress'),
]
