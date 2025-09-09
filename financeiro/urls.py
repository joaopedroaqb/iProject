from django.urls import path
from . import views

urlpatterns = [
    path("cadastrar/", views.cadastrar_financeiro, name="cadastrar_financeiro"),
    path("consultar/", views.consultar_financeiro, name="consultar_financeiro"),
    path("editar/<int:id>/", views.editar_financeiro, name="editar_financeiro"),
]
