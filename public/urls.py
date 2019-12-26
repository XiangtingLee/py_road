app_name = 'public'

from django.conf.urls import url
from . import views

urlpatterns = [
    url('^proxy/$', views.proxy_view, name='showProxy'),
    url('^getProxy/$', views.proxy_get, name='getProxy'),
    url('^uploadProxy/$', views.proxy_upload, name='uploadProxy'),
    url('^changeProxy/$', views.proxy_change, name='changeProxy'),
    url('^checkProxy/$', views.proxy_check, name='checkProxy'),
]
