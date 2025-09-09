# fatura/views.py
from __future__ import annotations

import json
from decimal import Decimal

from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_GET, require_POST
from django.db.models import Q
from django.db import transaction
from django.utils.timezone import now

from cadastro.models import Cliente
from controleOS.models import OrdemServico


# ------------ Utils ------------
def _parse_bool_param(val):
    """'True'/'False' (sim/não etc.) -> bool; None quando vazio/ausente."""
    if val is None:
        return None
    s = str(val).strip().lower()
    if s in ("true", "1", "t", "sim", "yes", "y"):
        return True
    if s in ("false", "0", "f", "nao", "não", "no", "n"):
        return False
    return None


# ------------ Endpoints ------------
@require_GET
def consultar_fatura(request):
    """
    GET /fatura/consultar/?cliente=<id>&inicio=YYYY-MM-DD&fim=YYYY-MM-DD&faturado=(True|False|)
    - Cliente e período são obrigatórios
    - Status alvo: concluído (aceita 'concluido', 'Concluído', 'Concluido')
    - 'faturado' opcional: True/False/omitido (Todos)
    - Intervalo por DATA (sem horário) em: data_solicitacao OR data_inicio OR data_final
    """
    cliente_id = request.GET.get("cliente")
    inicio_str = request.GET.get("inicio")
    fim_str = request.GET.get("fim")
    faturado_str = request.GET.get("faturado")  # "", "True" ou "False"

    if not cliente_id or not inicio_str or not fim_str:
        return JsonResponse({"erro": "Parâmetros obrigatórios: cliente, inicio, fim."}, status=400)

    try:
        cliente = Cliente.objects.get(pk=cliente_id)
    except Cliente.DoesNotExist:
        return JsonResponse({"erro": "Cliente não encontrado."}, status=404)

    dt_inicio = parse_date(inicio_str)
    dt_fim = parse_date(fim_str)
    if not dt_inicio or not dt_fim or dt_inicio > dt_fim:
        return JsonResponse({"erro": "Período inválido."}, status=400)

    faturado = _parse_bool_param(faturado_str)

    # Aceitar valores "errados" que podem estar no BD
    CONCLUIDO_VARIANTS = ["concluido", "Concluído", "Concluido"]

    # Base: cliente + status concluído (+ faturado se informado)
    base = OrdemServico.objects.filter(cliente=cliente, status__in=CONCLUIDO_VARIANTS).select_related("cliente")
    if faturado is not None:
        base = base.filter(faturado=faturado)

    # Contagens por campo (por DATA, sem horário)
    qs_solic = base.filter(data_solicitacao__date__gte=dt_inicio, data_solicitacao__date__lte=dt_fim)
    qs_inicio = base.filter(data_inicio__date__gte=dt_inicio,       data_inicio__date__lte=dt_fim)
    qs_final = base.filter(data_final__date__gte=dt_inicio,        data_final__date__lte=dt_fim)

    ids_solic = list(qs_solic.values_list("id", flat=True))
    ids_inicio = list(qs_inicio.values_list("id", flat=True))
    ids_final = list(qs_final.values_list("id", flat=True))

    # União (distinct)
    qs = (qs_solic | qs_inicio | qs_final).distinct().order_by("data_inicio", "data_solicitacao", "id")
    ids_union = list(qs.values_list("id", flat=True))

    # Prints no console (útil pra depurar)
    print("[FATURA] cliente_id=", cliente_id, "periodo=", inicio_str, "->", fim_str, "faturado=", faturado_str)
    print("[FATURA] counts: solic=", len(ids_solic), "inicio=", len(ids_inicio), "final=", len(ids_final), "union=", len(ids_union))
    print("[FATURA] ids_solic:", ids_solic)
    print("[FATURA] ids_inicio:", ids_inicio)
    print("[FATURA] ids_final:", ids_final)
    print("[FATURA] ids_union:", ids_union)

    resultados = []
    soma_horas = Decimal("0.00")
    soma_total = Decimal("0.00")

    for os in qs:
        horas = Decimal(os.horas_consumidas or 0)
        total = Decimal(os.total_faturar or 0)
        soma_horas += horas
        soma_total += total
        resultados.append({
            "id": os.id,
            "executante": os.executante or "",
            "solicitante": os.solicitante or "",
            "data_solicitacao": (os.data_solicitacao.date().isoformat() if os.data_solicitacao else ""),
            "problema": os.problema or "",
            "inicio": os.data_inicio.isoformat() if os.data_inicio else "",
            "fim": os.data_final.isoformat() if os.data_final else "",
            "horas": f"{horas:.2f}",
            "total": f"{total:.2f}",
        })

    return JsonResponse({
        "cliente": {
            "id": cliente.id,
            "razao_social": cliente.razao_social,
            "cpf_cnpj": cliente.cpf_cnpj,
            "endereco": cliente.endereco,
        },
        "periodo": {"inicio": dt_inicio.isoformat(), "fim": dt_fim.isoformat()},
        "faturado": faturado,   # True/False/None
        "os": resultados,       # <<< array para o front
        "totais": {"total_horas": f"{soma_horas:.2f}", "total_geral": f"{soma_total:.2f}"},
        "debug": {
            "counts": {
                "por_data_solicitacao": len(ids_solic),
                "por_data_inicio": len(ids_inicio),
                "por_data_final": len(ids_final),
                "uniao": len(ids_union),
            },
            "ids": {
                "solicitacao": ids_solic,
                "inicio": ids_inicio,
                "final": ids_final,
                "union": ids_union,
            }
        }
    }, json_dumps_params={"ensure_ascii": False})


@require_POST
def fechar_fatura(request):
    """
    POST /fatura/fechar/
    Body JSON:
      - inicio: "YYYY-MM-DD"
      - fim: "YYYY-MM-DD"
      - cliente: <id> (opcional se todos_clientes=true)
      - todos_clientes: true/false (default: false)

    Marca como faturadas as OS com status concluído no período (apenas faturado=False).
    Usa o MESMO critério de período (por DATA) da consulta.
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"erro": "JSON inválido."}, status=400)

    inicio_str = data.get("inicio")
    fim_str = data.get("fim")
    todos_clientes = bool(data.get("todos_clientes", False))
    cliente_id = data.get("cliente")

    if not inicio_str or not fim_str:
        return JsonResponse({"erro": "Parâmetros obrigatórios: inicio, fim."}, status=400)

    dt_inicio = parse_date(inicio_str)
    dt_fim = parse_date(fim_str)
    if not dt_inicio or not dt_fim or dt_inicio > dt_fim:
        return JsonResponse({"erro": "Período inválido."}, status=400)

    CONCLUIDO_VARIANTS = ["concluido", "Concluído", "Concluido"]

    base = OrdemServico.objects.filter(status__in=CONCLUIDO_VARIANTS, faturado=False).select_related("cliente")
    if not todos_clientes:
        if not cliente_id:
            return JsonResponse({"erro": "Informe 'cliente' ou use 'todos_clientes=true'."}, status=400)
        try:
            cliente = Cliente.objects.get(pk=cliente_id)
        except Cliente.DoesNotExist:
            return JsonResponse({"erro": "Cliente não encontrado."}, status=404)
        base = base.filter(cliente=cliente)

    qs = (base.filter(data_solicitacao__date__gte=dt_inicio, data_solicitacao__date__lte=dt_fim) |
          base.filter(data_inicio__date__gte=dt_inicio,       data_inicio__date__lte=dt_fim) |
          base.filter(data_final__date__gte=dt_inicio,        data_final__date__lte=dt_fim)
         ).distinct()

    afetadas = 0
    total_horas = Decimal("0.00")
    total_valor = Decimal("0.00")
    for os in qs:
        total_horas += Decimal(os.horas_consumidas or 0)
        total_valor += Decimal(os.total_faturar or 0)

    if qs.exists():
        with transaction.atomic():
            afetadas = qs.update(faturado=True, data_faturamento=now().date())

    return JsonResponse({
        "status": "sucesso",
        "afetadas": afetadas,
        "totais": {"total_horas": f"{total_horas:.2f}", "total_valor": f"{total_valor:.2f}"},
    })
