from django.db import models
from django.utils import timezone

# 1. DEFINIÇÕES DE ESCOLHA (CONSTANTES)
# Aqui centralizamos os valores possíveis para garantir consistência.
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

    # 2. CAMPOS DO MODELO
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

    # 3. LÓGICA DE NEGÓCIO: STATUS DINÂMICO
    def get_status(self):
        """
        EXPLICAÇÃO DA LÓGICA DE ATRASO:
        O sistema não altera o campo 'status' no banco de dados automaticamente 
        quando uma tarefa vence. Em vez disso, calculamos o status em tempo real.
        
        A regra é: se a tarefa não estiver 'concluido' E o momento atual (now)
        for maior que a 'due_date', o status exibido será 'atrasado'.
        Isso evita a necessidade de rodar tarefas agendadas (cron jobs) no servidor
        para atualizar o status de cada tarefa minuto a minuto.
        """
        now = timezone.now()
        if self.status != 'concluido' and now > self.due_date:
            return 'atrasado'
        return self.status

    # 4. LÓGICA DE TAREFAS PRÓXIMAS (UPCOMING)
    def is_upcoming(self):
        now = timezone.now()
        # Verifica se o início da tarefa está no futuro próximo (até 30 min)
        return self.start_time > now and self.start_time <= (now + timezone.timedelta(minutes=30))

    # 5. LÓGICA DE TAREFAS URGENTES (URGENT)
    def is_urgent(self):
        """
        Calcula se a tarefa entra na janela de perigo (vence em até 2 horas).
        A lógica é: não concluída + ainda não passou do prazo + prazo cai em 2h.
        """
        now = timezone.now()
        return self.status != 'concluido' and now < self.due_date and now >= (self.due_date - timezone.timedelta(hours=2))

    # 6. MÉTODO REPRESENTATIVO
    def __str__(self):
        return self.title