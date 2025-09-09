from django.contrib import admin
from .models import OrdemServico

@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'executante',
        'cliente',
        'solicitante',
        'previsao',
        'status',
        'faturado',
        'data_solicitacao',
        'horas_consumidas', 
        'total_faturar',
        'data_faturamento'
    )
    list_filter = ('executante', 'cliente', 'status', 'faturado')
    search_fields = ('cliente__razao_social', 'solicitante', 'problema')
