from . import views
from django.urls import path
urlpatterns = [
    path('makeSale/', views.register_sale),
    path('makeRefund/', views.refund_sale)
]
