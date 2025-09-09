from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime, parse_date
from .models import OrdemServico
from cadastro.models import Cliente
from datetime import timedelta
from django.db.models import Q

# ========== LISTAR OS ==========
def listar_os(request):
    cliente_nome = request.GET.get("cliente", "").strip().lower()
    status = request.GET.get("status", "").strip()
    faturado = request.GET.get("faturado", "").strip()

    ordens = OrdemServico.objects.select_related('cliente')

    if cliente_nome:
        ordens = ordens.filter(cliente__razao_social__icontains=cliente_nome)
    if status:
        ordens = ordens.filter(status=status)
    if faturado == "True":
        ordens = ordens.filter(faturado=True)
    elif faturado == "False":
        ordens = ordens.filter(faturado=False)

    html = """
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Executante</th>
          <th>Cliente</th>
          <th>Solicitante</th>
          <th>Solicitado em</th>
          <th>Problema</th>
          <th>Início</th>
          <th>Final</th>
          <th>Horas</th>
          <th>Total R$</th>
          <th>Status</th>
          <th>Faturado</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
    """

    for os in ordens:
        html += f"""
        <tr data-id="{os.id}">
          <td>{os.id}</td>
          <td data-editable data-field="executante">{os.executante}</td>
          <td>{os.cliente.razao_social}</td>
          <td>{os.solicitante}</td>
          <td>{os.data_solicitacao.strftime('%d/%m/%Y') if os.data_solicitacao else ''}</td>
          <td>{os.problema}</td>
          <td data-editable data-field="data_inicio">{os.data_inicio.strftime('%d/%m/%Y %H:%M') if os.data_inicio else ''}</td>
          <td data-editable data-field="data_final">{os.data_final.strftime('%d/%m/%Y %H:%M') if os.data_final else ''}</td>
          <td>{os.horas_consumidas or ''}</td>
          <td>{os.total_faturar or ''}</td>
          <td data-editable data-field="status">{os.get_status_display()}</td>
          <td data-editable data-field="faturado">{'Sim' if os.faturado else 'Não'}</td>
          <td>
            <button class="btn-edit">Editar</button>
            <button class="btn-save" data-id="{os.id}" style="display:none;">Salvar</button>
          </td>
        </tr>
        """

    html += "</tbody></table>"
    return HttpResponse(html)

# ========== CADASTRAR OS ==========
@csrf_exempt
def cadastrar_os(request):
    if request.method == 'POST':
        try:
            data_inicio = parse_datetime(request.POST.get('data_inicio'))
            data_final = parse_datetime(request.POST.get('data_final'))
            cliente_id = request.POST.get('cliente_id') or request.POST.get('cliente')
            cliente = Cliente.objects.get(id=cliente_id)

            horas_consumidas = None
            total_faturar = None

            if data_inicio and data_final:
                delta = data_final - data_inicio
                horas_consumidas = round(delta.total_seconds() / 3600, 2)
                if cliente.modalidade.lower() == 'hora':
                    total_faturar = round(horas_consumidas * float(cliente.valor_cobranca), 2)

            OrdemServico.objects.create(
                executante=request.POST.get('executante', 'Artur'),
                cliente=cliente,
                solicitante=request.POST.get('solicitante'),
                data_solicitacao=parse_date(request.POST.get('data_solicitacao')),
                previsao=parse_date(request.POST.get('previsao')),
                problema=request.POST.get('problema'),
                data_inicio=data_inicio,
                data_final=data_final,
                status=request.POST.get('status', 'nao_iniciado'),
                faturado=request.POST.get('faturado') == 'True',
                data_faturamento=parse_date(request.POST.get('data_faturamento')),
                horas_consumidas=horas_consumidas,
                total_faturar=total_faturar
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            print("ERRO AO CADASTRAR OS:", str(e))
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método inválido'}, status=400)

# ========== EDITAR OS INLINE ==========
@csrf_exempt
def editar_os(request, id):
    if request.method == 'POST':
        try:
            os = OrdemServico.objects.get(pk=id)

            # Campos editáveis
            if 'executante' in request.POST:
                os.executante = request.POST['executante']
            if 'status' in request.POST:
                os.status = request.POST['status']
            if 'faturado' in request.POST:
                os.faturado = request.POST['faturado'] == 'True'
            if 'data_inicio' in request.POST:
                os.data_inicio = parse_datetime(request.POST['data_inicio']) or None
            if 'data_final' in request.POST:
                os.data_final = parse_datetime(request.POST['data_final']) or None

            # Recalcular horas e total se datas válidas
            if os.data_inicio and os.data_final:
                delta = os.data_final - os.data_inicio
                os.horas_consumidas = round(delta.total_seconds() / 3600, 2)

                if os.cliente.modalidade.lower() == "hora":
                    os.total_faturar = round(os.horas_consumidas * float(os.cliente.valor_cobranca), 2)
                else:
                    os.total_faturar = 0
            else:
                os.horas_consumidas = None
                os.total_faturar = None

            os.save()
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método inválido'}, status=400)

# ========== API DE CLIENTES ==========
def clientes_json(request):
    clientes = Cliente.objects.all().values("id", "razao_social", "cpf_cnpj")
    return JsonResponse(list(clientes), safe=False)

# ========== VALOR E MODALIDADE DO CLIENTE ==========
def cliente_valor(request, id):
    try:
        cliente = Cliente.objects.get(pk=id)
        return JsonResponse({
            'valor': float(cliente.valor_cobranca),
            'modalidade': cliente.modalidade.lower()
        })
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Cliente não encontrado'}, status=404)

# ========== FORMULÁRIO HTML PARA RECARREGAMENTO ==========
def formulario_controle_os(request):
    clientes = Cliente.objects.all()
    return render(request, 'partials/formulario_controle_os.html', {'clientes': clientes})
