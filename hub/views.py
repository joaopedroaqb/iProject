from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from cadastro.models import Cliente
from django.contrib.auth.models import User

@login_required
@user_passes_test(lambda u: u.is_staff)
def hub_view(request):
    clientes = Cliente.objects.all()
    usuarios = User.objects.all()
    return render(request, 'hub/hub.html', {
        'clientes': clientes,
        'usuarios': usuarios,
    })
