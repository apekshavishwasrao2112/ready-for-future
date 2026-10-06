from django.urls import path

from . import views


app_name = 'interview'

urlpatterns = [
    path('', views.questions, name='questions'),
    path('practice/', views.practice, name='practice'),
]
