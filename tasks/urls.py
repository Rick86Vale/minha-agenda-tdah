# tasks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('criar/', views.task_create, name='task_create'),
    path('api/tasks/', views.task_data, name='task_data'),
    path('complete/<int:task_id>/', views.complete_task, name='complete_task'), 
]