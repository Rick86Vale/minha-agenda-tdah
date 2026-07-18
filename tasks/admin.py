from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'start_time', 'due_date', 'status')
    list_filter = ('status', 'priority')
    search_fields = ('title',)

    