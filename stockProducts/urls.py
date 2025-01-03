from django.urls import path, include
from . import views

urlpatterns = [
    path('create_product/', views.create_product),
    path('delete_product/', views.delete_product)
]