"""pyroad URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls import url
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url('^$', views.main, name='main'),
    url('^index$', views.index, name='index'),
    url('^login$', views.login_view, name='login'),
    url('^login_act$', views.login_action, name='login_act'),
    url('^reg$', views.reg_view, name='reg'),
    url('^reg_act$', views.reg_action, name='reg_act'),
    path('public/', include('public.urls', namespace='public')),
]
