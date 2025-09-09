from django.db import models
from cadastro.models import Cliente

class OrdemServico(models.Model):
    executante = models.CharField(max_length=100, default='Artur')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    solicitante = models.CharField(max_length=100)
    data_solicitacao = models.DateTimeField("Data de Solicitação", null=True, blank=True)
    previsao = models.DateField(null=True, blank=True)  # Previsão

    problema = models.TextField()
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_final = models.DateTimeField(null=True, blank=True)

    STATUS_CHOICES = [
        ('nao_iniciado', 'Não Iniciado'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='nao_iniciado'
    )

    faturado = models.BooleanField(default=False)
    data_faturamento = models.DateField(null=True, blank=True)
    horas_consumidas = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    total_faturar = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    def __str__(self):
        return f"OS #{self.id} - {self.cliente.razao_social}"
