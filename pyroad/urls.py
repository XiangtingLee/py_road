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

from user.views import login_act, logout_act, reg_act, reset_act, reg_guide
from . import views

urlpatterns = [
    path('site/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
    path('log/', include('log.urls', namespace='log')),
    path('api/', include('api.urls', namespace='api')),
    path('public/', include('public.urls', namespace='public')),
    path('user/', include('user.urls', namespace='user')),
    path('position/', include('position.urls', namespace='position')),
    path('wuhan2020/', include('wuhan2020.urls', namespace='wuhan2020')),
    url('', include('social_django.urls', namespace='social'), name='social'),
    url('^$', views.main, name='main'),
    url('^index$', views.index, name='index'),
    url('^login$', login_act, name='login'),
    url('^reset$', reset_act, name='reset'),
    url('^logout$', logout_act, name='logout'),
    url('^reg$', reg_act, name='reg'),
    url('^reg/guide$', reg_guide, name='reg_guide'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
