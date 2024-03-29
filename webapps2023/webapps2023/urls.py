"""webapps2023 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from register.views import CustomTemplateView, CustomLoginView, CustomLoginViewAdmin, CustomPasswordChangeViewAdmin

urlpatterns = [
    # Conversion REST API
    path('conversion/', include('conversion.urls')),

    # Web App
    path('admin/login/', CustomLoginViewAdmin.as_view(), name='admin_login'),
    path('admin/password_change/', CustomPasswordChangeViewAdmin.as_view(), name='admin_password_change'),
    path('admin/', admin.site.urls),
    path('', CustomTemplateView.as_view(template_name='home.html'), name='home'),
    path('about_us/', CustomTemplateView.as_view(template_name='about_us.html'), name='about_us'),
    path('register/login/', CustomLoginView.as_view(), name='user_login'),
    path('register/', include('django.contrib.auth.urls')),
    path('register/', include('register.urls')),
    path('payapp/', include('payapp.urls'))
]
