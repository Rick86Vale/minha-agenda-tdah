# tasks/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Task
from .forms import TaskForm

def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('calendar')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

def calendar_view(request):
    now = timezone.now()
    
    # Histórico (Esquerda): Passadas ou Concluídas
    past = Task.objects.filter(start_time__lt=now).order_by('-start_time')
    history_tasks = Paginator(past, 10).get_page(request.GET.get('page_left'))
    
    # Próximas (Direita): Futuras e Pendentes
    future = Task.objects.filter(start_time__gte=now, status=False).order_by('start_time')
    next_tasks = Paginator(future, 10).get_page(request.GET.get('page_right'))
    
    return render(request, 'tasks/calendar.html', {
        'next_tasks': next_tasks, 
        'history_tasks': history_tasks
    })

@require_POST
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.status = True
    task.save()
    return redirect('calendar')

def task_data(request):
    return JsonResponse([
        {'title': t.title, 'start': t.start_time.isoformat(), 'end': t.due_date.isoformat(), 'color': "#ff4343" if t.priority == 'H' else '#10ac84'}
        for t in Task.objects.all()
    ], safe=False)