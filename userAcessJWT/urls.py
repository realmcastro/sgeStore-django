from django.urls import path, include
from . import views
urlpatterns = [
    path('create_user/', views.create_user),
    path('login/', views.login)
]