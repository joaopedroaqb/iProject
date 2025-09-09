from django.urls import path
from .views import (
    cadastrar_os,
    listar_os,
    clientes_json,
    cliente_valor,  
    editar_os,
)
from django.urls import path
from . import views

urlpatterns = [
    path('cadastrar/', cadastrar_os),
    path('listar/', listar_os),
    path('clientes/', clientes_json),
    path('cadastro/cliente/<int:id>/valor/', cliente_valor), 
    path('cadastro/cliente/<int:id>/valor/', cliente_valor),
    path('cliente/<int:id>/valor/', cliente_valor, name='cliente_valor'),
    path('controleOS/editar/<int:id>/', editar_os),
    path("editar/<int:id>/", editar_os, name="editar_os"),
     path('controleOS/form/', views.formulario_controle_os, name='formulario_controle_os'),
     path('formulario/', views.formulario_controle_os, name='formulario_controle_os'),
]

