from django.urls import path

from . import views


app_name = 'resumes'

urlpatterns = [
    path('', views.resume_list, name='list'),
    path('list/', views.resume_list, name='list_page'),
    path('upload/', views.upload_resume, name='upload'),
    path('<int:resume_id>/file/', views.download_resume, name='download'),
    path('<int:resume_id>/', views.resume_result, name='result'),
]
