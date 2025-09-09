# fatura/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('consultar/', views.consultar_fatura, name='fatura_consultar'),
    path('fechar/', views.fechar_fatura, name='fatura_fechar'),  # opcional, mas recomendado
]
