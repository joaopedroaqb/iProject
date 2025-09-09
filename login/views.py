from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect("/hub/" if user.is_staff else "/user/")
        return render(request, "login/login.html", {"error": "Credenciais inválidas."})
    return render(request, "login/login.html")

@login_required
def user_home(request):
    if request.user.is_staff:
        return redirect("/hub/")
    return render(request, "login/user_home.html")

def logout_view(request):
    logout(request)
    return redirect("/")
