from django.urls import path
from .views import login_view, logout_view, user_home

urlpatterns = [
    path('', login_view),
    path('logout/', logout_view),
    path('user/', user_home),
]
