from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .forms import LancamentoFinanceiroForm
from .models import LancamentoFinanceiro
from cadastro.models import Cliente
import json
from datetime import datetime
from decimal import Decimal


# ========== CADASTRO ==========
def cadastrar_financeiro(request):
    if request.method == 'POST':
        form = LancamentoFinanceiroForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("OK")
        else:
            return HttpResponseBadRequest("Formulário inválido: " + str(form.errors))
    return HttpResponseBadRequest("Método não permitido.")


# ========== CONSULTA + TOTAL ==========
def consultar_financeiro(request):
    tipo = request.GET.get("tipo")
    situacao = request.GET.get("situacao")
    inicio = request.GET.get("inicio")
    fim = request.GET.get("fim")

    queryset = LancamentoFinanceiro.objects.select_related("cliente").all()

    if tipo:
        queryset = queryset.filter(tipo=tipo)

    if situacao and situacao != "todos":
        if situacao == "aberto":
            queryset = queryset.filter(data_baixa__isnull=True)
        elif situacao == "baixado":
            queryset = queryset.filter(data_baixa__isnull=False)

    if inicio:
        queryset = queryset.filter(vencimento__gte=inicio)
    if fim:
        queryset = queryset.filter(vencimento__lte=fim)

    dados = []
    total_receitas = Decimal("0.00")
    total_despesas = Decimal("0.00")

    for lanc in queryset:
        if lanc.tipo == "Receita":
            total_receitas += lanc.valor
        elif lanc.tipo == "Despesa":
            total_despesas += lanc.valor

        dados.append({
            "id": lanc.id,
            "tipo": lanc.tipo,
            "cliente": lanc.cliente.razao_social if lanc.cliente else "—",
            "vencimento": lanc.vencimento.strftime("%Y-%m-%d"),
            "valor": str(lanc.valor),
            "data_baixa": lanc.data_baixa.strftime("%Y-%m-%d") if lanc.data_baixa else "",
            "situacao": "Baixado" if lanc.data_baixa else "Em Aberto",
            "codigo_barras": lanc.codigo_barras or "",
            "observacao": lanc.observacao or ""
        })

    return JsonResponse({
        "resultados": dados,
        "totais": {
            "receitas": str(total_receitas),
            "despesas": str(total_despesas),
            "saldo": str(total_receitas - total_despesas)
        }
    })


# ========== EDIÇÃO ==========
@csrf_exempt
@require_http_methods(["POST"])
def editar_financeiro(request, id):
    body = json.loads(request.body)
    lancamento = get_object_or_404(LancamentoFinanceiro, id=id)

    # Atualiza os campos editáveis
    lancamento.tipo = body.get("tipo", lancamento.tipo)
    lancamento.valor = body.get("valor", lancamento.valor)
    lancamento.vencimento = datetime.strptime(body.get("vencimento"), "%Y-%m-%d").date()
    data_baixa = body.get("data_baixa")
    lancamento.data_baixa = datetime.strptime(data_baixa, "%Y-%m-%d").date() if data_baixa else None

    lancamento.save()
    return JsonResponse({"status": "sucesso"})
