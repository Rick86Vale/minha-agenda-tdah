# tasks/forms.py
from django import forms
from .models import Task
from .models import LocalHoliday

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'start_time', 'due_date'] 
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class LocalHolidayForm(forms.ModelForm):
    class Meta:
        model = LocalHoliday
        fields = ['name', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }