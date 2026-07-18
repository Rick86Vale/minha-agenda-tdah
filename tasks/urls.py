from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('criar/', views.task_create, name='task_create'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('task/<int:task_id>/editar/', views.task_update, name='task_update'),
    path('task/<int:task_id>/excluir/', views.task_delete, name='task_delete'),
    path('api/tasks/', views.task_data, name='task_data'),
    path('complete/<int:task_id>/', views.complete_task, name='complete_task'),
]