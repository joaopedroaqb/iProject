from django import forms
from .models import LancamentoFinanceiro

class LancamentoFinanceiroForm(forms.ModelForm):
    class Meta:
        model = LancamentoFinanceiro
        fields = ['tipo', 'cliente', 'vencimento', 'valor', 'data_baixa', 'codigo_barras', 'observacao']
