# tasks/views.py 
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Task
from .forms import TaskForm

# 1. CRIAÇÃO DE TAREFAS
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('calendar')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

# 2. VISUALIZAÇÃO DO DASHBOARD/CALENDÁRIO
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

# 3. LÓGICA DE EXECUÇÃO DE TAREFAS
@require_POST
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.status = True
    task.save()
    return redirect('calendar')

# 4. API PARA O FULLCALENDAR
def task_data(request):
    return JsonResponse([
        {'title': t.title, 'start': t.start_time.isoformat(), 'end': t.due_date.isoformat(), 'color': "#ff4343" if t.priority == 'H' else '#10ac84'}
        for t in Task.objects.all()
    ], safe=False)

# 5. DETALHES DE TAREFA
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'tasks/task_detail.html', {'task': task})

# 6. EDIÇÃO DE TAREFAS
def task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})

# 7. EXCLUSÃO DE TAREFAS
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        return redirect('calendar')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})