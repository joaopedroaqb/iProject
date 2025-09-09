from django.db import models
from cadastro.models import Cliente

class LancamentoFinanceiro(models.Model):
    TIPO_CHOICES = (
        ('Receita', 'Receita'),
        ('Despesa', 'Despesa'),
    )

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    vencimento = models.DateField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_baixa = models.DateField(blank=True, null=True)
    codigo_barras = models.CharField(max_length=255, blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} - {self.cliente.razao_social} - R$ {self.valor}"
