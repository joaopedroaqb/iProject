from django.db import models

class Cliente(models.Model):
    TIPO_CHOICES = [
        ("Física", "Física"),
        ("Jurídica", "Jurídica"),
    ]

    MODALIDADE_CHOICES = [
        ("Contrato", "Contrato"),
        ("Hora", "Hora"),
        ("Projeto", "Projeto"),
    ]

    cpf_cnpj = models.CharField(max_length=20)
    razao_social = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    endereco = models.TextField()
    modalidade = models.CharField(max_length=10, choices=MODALIDADE_CHOICES)
    valor_cobranca = models.DecimalField(max_digits=10, decimal_places=2)
    data_faturamento = models.DateField()
    vencimento_dia = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Dia de Vencimento",
        help_text="Informe o dia do mês para vencimento (1 a 31)"
    )  

    def __str__(self):
        return self.razao_social
