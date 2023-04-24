from django.urls import path, re_path
from . import views

urlpatterns = [
    path('transfer/', views.balance_transfer, name='transfer'),
    path('request_payment/', views.payment_request, name='request_payment'),
    path('transactions/', views.transactions_list, name='transactions'),
    path('requests/', views.requests_list, name='requests'),
    re_path(r'^requests/(?P<pk>[0-9]+)/update_status/$', views.request_update_status,
            name='requests_update_status')
]
