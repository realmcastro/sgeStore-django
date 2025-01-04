from django.urls import path, include
from . import views

urlpatterns = [

    path('create_user/', views.create_user),
    path('login/', views.login),
    path('mod_pass/', views.update_password),
    path('delete_user/', views.delete_user),
    path('list_users/', views.list_users)

]