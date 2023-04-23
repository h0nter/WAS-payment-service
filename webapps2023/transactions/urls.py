from django.urls import path
from . import views

urlpatterns = [
    path('transfer/', views.balance_transfer, name='transfer'),
    path('request/', views.payment_request, name='request')
]
