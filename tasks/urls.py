from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('criar/', views.task_create, name='task_create'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('task/<int:task_id>/editar/', views.task_update, name='task_update'),
    path('task/<int:task_id>/excluir/', views.task_delete, name='task_delete'),
    path('api/tasks/', views.task_data, name='task_data'),
    path('task/<int:task_id>/start/', views.start_task, name='start_task'),
    path('task/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('tarefas/', views.task_list, name='task_list'),
    # Feriados
    path('api/feriados/', views.holiday_api, name='holiday_api'),
    path('feriados/', views.holiday_list, name='holiday_list'),
]