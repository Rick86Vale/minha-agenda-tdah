from django.db import models
from django.utils import timezone

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('L', 'Baixa'),
        ('M', 'Média'),
        ('H', 'Alta'),
    ]

    STATUS_CHOICES = [
        ('nao_iniciado', 'Não Iniciado'),
        ('iniciado', 'Iniciado'),
        ('pendente', 'Pendente'),
        ('concluido', 'Concluído'),
        ('atrasado', 'Atrasado'),
    ]

    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='nao_iniciado', 
        verbose_name="Status"
    )
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M', verbose_name="Prioridade")
    start_time = models.DateTimeField(verbose_name="Data de Início")
    due_date = models.DateTimeField(verbose_name="Data de Vencimento")
    reminder_sent = models.BooleanField(default=False, verbose_name="Lembrete Enviado")

    def get_status(self):
        """Retorna o status atual, calculando o atraso se necessário."""
        now = timezone.now()
        # Se não estiver concluído e a data de vencimento passou, é atrasado
        if self.status != 'concluido' and now > self.due_date:
            return 'atrasado'
        return self.status

    def is_upcoming(self):
        now = timezone.now()
        # Tarefa é considerada "próxima" se começa em até 30 minutos
        return self.start_time > now and self.start_time <= (now + timezone.timedelta(minutes=30))

    def __str__(self):
        return self.title