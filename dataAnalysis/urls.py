from . import views
from django.urls import path
urlpatterns = [
    path('dataSale/', views.sales_chart),
    path('getData/', views.daily_sales)
]
