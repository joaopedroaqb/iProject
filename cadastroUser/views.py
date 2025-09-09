from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_staff)
def cadastrar_usuario(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        username = request.POST.get("username")
        senha = request.POST.get("senha")
        is_admin = request.POST.get("is_admin") == "on"

        user = User.objects.create_user(
            username=username,
            email=email,
            password=senha,
            first_name=nome
        )
        user.is_staff = is_admin
        user.save()
        return redirect("/cadastroUser/listar/")

    return render(request, "cadastroUser/register.html")

@user_passes_test(lambda u: u.is_staff)
def listar_usuarios(request):
    usuarios = User.objects.all()
    return render(request, "cadastroUser/list_users.html", {"usuarios": usuarios})

from django.template.loader import render_to_string
from django.http import HttpResponse

@user_passes_test(lambda u: u.is_staff)
def tabela_usuarios(request):
    usuarios = User.objects.all()
    html = render_to_string("partials/tabela_usuarios.html", {"usuarios": usuarios})
    return HttpResponse(html)