from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'(?P<currency1>[a-zA-Z]{3})/(?P<currency2>[a-zA-Z]{3})/(?P<amount_of_currency1>[0-9]+(\.[0-9][0-9]?)?)$',
            views.ConversionView.as_view(),
            name='conversion_api')
]
