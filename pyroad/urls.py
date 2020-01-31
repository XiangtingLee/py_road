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

from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from . import views

urlpatterns = [
    path('site/', admin.site.urls),
    url('^$', views.main, name='main'),
    url('^index$', views.index, name='index'),
    url('^login$', views.login_act, name='login'),
    url('^logout$', views.logout_act, name='logout'),
    url('^reg$', views.reg_act, name='reg'),
    path('log/', include('log.urls', namespace='log')),
    path('public/', include('public.urls', namespace='public')),
    path('user/', include('user.urls', namespace='user')),
    path('position/', include('position.urls', namespace='position')),
    path('wuhan2020/', include('wuhan2020.urls', namespace='wuhan2020')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
