# tasks/views.py 
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import models
from .models import Task, LocalHoliday
from .forms import TaskForm

from datetime import timedelta 

import datetime
# feriados 
import holidays
from itertools import groupby
from operator import itemgetter
from .forms import LocalHolidayForm 
from itertools import groupby

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
    data_limite = now - timedelta(days=40)
    
    # 1. QuerySets
    past = Task.objects.filter(
        models.Q(status='concluido') | models.Q(due_date__lt=now),
        due_date__gte=data_limite
    ).order_by('-due_date')
    
    future = Task.objects.exclude(status='concluido').filter(
        due_date__gte=now
    ).order_by('start_time')
    
    # 2. Paginação Independente
    # Paginador Esquerda (Histórico)
    paginator_left = Paginator(past, 6)
    page_left = request.GET.get('page_left')
    history_tasks = paginator_left.get_page(page_left)
    
    # Paginador Direita (Próximas)
    paginator_right = Paginator(future, 6)
    page_right = request.GET.get('page_right')
    next_tasks = paginator_right.get_page(page_right)
    
    return render(request, 'tasks/calendar.html', {
        'next_tasks': next_tasks, 
        'history_tasks': history_tasks,
        # Passamos a página atual para o template para ajudar a compor os links
        'page_left': page_left,
        'page_right': page_right
    })

# 3. LÓGICA DE EXECUÇÃO DE TAREFAS
@require_POST
def start_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.status = 'iniciado' 
    task.save()
    return redirect('task_detail', task_id=task.id)

@require_POST
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.status = 'concluido'
    task.save()
    return redirect('calendar')

# 4. API PARA O FULLCALENDAR
def task_data(request):
    # Mapeamento de status para as cores CSS que definimos
    color_map = {
        'nao_iniciado': '#95a5a6',
        'iniciado': '#3498db',
        'pendente': '#e67e22',
        'concluido': '#10ac84',
        'atrasado': '#ff4343'
    }
    
    return JsonResponse([
        {
            'title': t.title, 
            'start': t.start_time.isoformat(), 
            'end': t.due_date.isoformat(), 
            'color': color_map.get(t.get_status(), '#95a5a6') # Pega a cor ou usa cinza como padrão
        }
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
    # Tenta pegar o 'next' da query string
    next_url = request.GET.get('next') or request.POST.get('next')
    
    # LÓGICA DE SEGURANÇA:
    # Se o next_url for a página da própria tarefa, descartamos ele 
    # para evitar o erro 404 pós-exclusão.
    if next_url and f'/task/{task_id}/' in next_url:
        next_url = 'calendar'

    if request.method == 'POST':
        task.delete()
        # Se next_url for um nome de view (ex: 'calendar'), o redirect resolve.
        # Se for uma URL (ex: '/lista/'), o redirect também resolve.
        return redirect(next_url if next_url else 'calendar')
    
    return render(request, 'tasks/task_confirm_delete.html', {
        'task': task,
        'next': next_url 
    })

# 8. LISTA DE TAREFAS
def task_list(request):
    tasks = Task.objects.all().order_by('due_date')
    
    # Filtros
    status_filter = request.GET.get('status')
    month_filter = request.GET.get('month')
    urgent_filter = request.GET.get('urgent')
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    if month_filter:
        tasks = tasks.filter(due_date__month=month_filter)
        
    if urgent_filter == 'true':
        # Filtramos em Python, já que is_urgent é um método do modelo
        tasks = [t for t in tasks if t.is_urgent()]
        
    # Paginação: 10 tarefas por página
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'tasks/task_list.html', {'tasks': page_obj})

# 9. FERIADOS NACIONAIS
def holiday_api(request):
    # 1. Nacionais
    br_holidays = holidays.Brazil(years=2026)
    eventos = [{'title': name, 'start': date.strftime('%Y-%m-%d'), 'display': 'background', 'backgroundColor': '#ff7675'} 
               for date, name in br_holidays.items()]
    
    # 2. Locais (do seu novo modelo)
    locais = LocalHoliday.objects.all()
    for h in locais:
        eventos.append({
            'title': h.name,
            'start': h.date.strftime('%Y-%m-%d'),
            'display': 'background',
            'backgroundColor': '#ffeaa7' # Cor diferente para feriado local
        })
    
    return JsonResponse(eventos, safe=False)



def holiday_list(request):
    # 1. Feriados Nacionais
    br_holidays = holidays.Brazil(years=2026)
    
    # 2. Feriados Locais (convertendo para o mesmo formato do br_holidays)
    local_holidays = LocalHoliday.objects.all()
    # Adicionamos os locais ao dicionário de feriados
    for h in local_holidays:
        br_holidays[h.date] = h.name
        
    # Ordena tudo por data
    holiday_data = sorted(br_holidays.items())
    
    # Agrupa por mês
    grouped_holidays = []
    for month, group in groupby(holiday_data, key=lambda x: x[0].strftime('%B').capitalize()):
        grouped_holidays.append((month, list(group)))
    
    return render(request, 'tasks/holiday_list.html', {'holidays': grouped_holidays})

# Feriados Locais
def holiday_crud(request):
    holidays = LocalHoliday.objects.all().order_by('date')
    if request.method == 'POST':
        form = LocalHolidayForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('holiday_crud')
    else:
        form = LocalHolidayForm()
    return render(request, 'tasks/holiday_crud.html', {'holidays': holidays, 'form': form})

def holiday_delete(request, holiday_id):
    holiday = get_object_or_404(LocalHoliday, id=holiday_id)
    holiday.delete()
    return redirect('holiday_crud')

