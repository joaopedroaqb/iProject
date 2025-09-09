from django.urls import path
from .views import hub_view

urlpatterns = [
    path('', hub_view),
]
