from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from .models import Cliente

# Verificação se o usuário é staff
is_staff_check = user_passes_test(lambda u: u.is_staff)

# =========================
# CADASTRAR CLIENTE
# =========================
@is_staff_check
def cadastrar_cliente(request):
    if request.method == "POST":
        Cliente.objects.create(
            cpf_cnpj=request.POST.get("cpf_cnpj"),
            razao_social=request.POST.get("razao_social"),
            tipo=request.POST.get("tipo"),
            endereco=request.POST.get("endereco"),
            modalidade=request.POST.get("modalidade"),
            valor_cobranca=request.POST.get("valor_cobranca"),
            data_faturamento=request.POST.get("data_faturamento"),
            vencimento_dia=request.POST.get("vencimento_dia"),
        )
        return redirect("/cadastro/listar/")
    return render(request, "cadastro/cadastro_cliente.html")

# =========================
# LISTAR CLIENTES (com template completo)
# =========================
@is_staff_check
def listar_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, "cadastro/listar_clientes.html", {"clientes": clientes})

# =========================
# ATUALIZAR TABELA AJAX
# =========================
@is_staff_check
def tabela_clientes(request):
    clientes = Cliente.objects.all()
    html = render_to_string('partials/tabela_clientes.html', {'clientes': clientes})
    return HttpResponse(html)

# =========================
# EXCLUIR CLIENTE
# =========================
@is_staff_check
def excluir_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == "POST":
        cliente.delete()
    return redirect('/hub/')

# =========================
# EDITAR CLIENTE (usado via POST no hub)
# =========================
@is_staff_check
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == "POST":
        cliente.cpf_cnpj = request.POST.get("cpf_cnpj")
        cliente.razao_social = request.POST.get("razao_social")
        cliente.tipo = request.POST.get("tipo")
        cliente.modalidade = request.POST.get("modalidade")
        cliente.endereco = request.POST.get("endereco")
        cliente.valor_cobranca = request.POST.get("valor_cobranca")
        cliente.data_faturamento = request.POST.get("data_faturamento")
        cliente.vencimento_dia = request.POST.get("vencimento_dia")
        cliente.save()
        return redirect('/hub/')
    
    # Usado apenas se for acesso tradicional (não necessário no hub)
    return render(request, "cadastro/editar_cliente.html", {"cliente": cliente})

# =========================
# DETALHES DO CLIENTE (usado via fetch no hub para preencher o form)
# =========================
@is_staff_check
def detalhes_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    return JsonResponse({
        "cpf_cnpj": cliente.cpf_cnpj,
        "razao_social": cliente.razao_social,
        "tipo": cliente.tipo,
        "modalidade": cliente.modalidade,
        "endereco": cliente.endereco,
        "valor_cobranca": str(cliente.valor_cobranca),
        "data_faturamento": cliente.data_faturamento.strftime("%Y-%m-%d") if cliente.data_faturamento else "",
        "vencimento_dia": cliente.vencimento_dia or "",  # <-- Aqui está o campo corrigido
    })

from django.http import JsonResponse
from .models import Cliente

def clientes_json(request):
    clientes = Cliente.objects.all().values("id", "razao_social", "cpf_cnpj")
    return JsonResponse(list(clientes), safe=False)

from django.shortcuts import render
from cadastro.models import Cliente

def formulario_controle_os(request):
    clientes = Cliente.objects.all()
    return render(request, 'partials/formulario_controle_os.html', {'clientes': clientes})