from django.contrib import admin
from .models import LancamentoFinanceiro

@admin.register(LancamentoFinanceiro)
class LancamentoFinanceiroAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'cliente', 'vencimento', 'valor', 'data_baixa')
    list_filter = ('tipo', 'data_baixa')
    search_fields = ('cliente__nome', 'codigo_barras', 'observacao')
