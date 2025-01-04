from django.urls import path, include
from . import views

urlpatterns = [
    path('create_product/', views.create_product),
    path('delete_product/', views.delete_product),
    path('list_product/', views.list_product),
    path('update_product/', views.update_product)
]