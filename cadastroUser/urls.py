from django.urls import path
from .views import cadastrar_usuario, listar_usuarios

from .views import cadastrar_usuario, listar_usuarios, tabela_usuarios

urlpatterns = [
    path('cadastrar/', cadastrar_usuario),
    path('listar/', listar_usuarios),
    path('listar/tabela/', tabela_usuarios), 
]
