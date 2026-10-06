from django.urls import path

from . import views


app_name = 'learning'

urlpatterns = [
    path('', views.roadmap, name='roadmap'),
    path('day/<int:day_number>/', views.day_detail, name='day'),
]
