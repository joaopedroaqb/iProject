from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('login.urls')),
    path('hub/', include('hub.urls')),
    path('cadastro/', include('cadastro.urls')),
    path('cadastroUser/', include('cadastroUser.urls')),  # ← esse aqui depende do arquivo urls.py existir
    path('controleOS/', include('controleOS.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('fatura/', include('fatura.urls')),
]
