from django.urls import path
from .views import (
    cadastrar_cliente,
    listar_clientes,
    tabela_clientes,
    excluir_cliente,
    editar_cliente,
    detalhes_cliente,  # novo
)

urlpatterns = [
    path('cadastrar/', cadastrar_cliente),
    path('listar/', listar_clientes),
    path('listar/tabela/', tabela_clientes),
    path('editar/<int:id>/', editar_cliente),
    path('excluir/<int:id>/', excluir_cliente),
    path('detalhes/<int:id>/', detalhes_cliente),  # usado pelo JS
]
