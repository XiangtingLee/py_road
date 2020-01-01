app_name = 'public'

from django.conf.urls import url
from . import views

urlpatterns = [
    url('^proxy/view/$', views.proxy_view, name='proxy_view'),
    url('^proxy/data/$', views.proxy_data, name='proxy_data'),
    url('^proxy/upload/$', views.proxy_upload, name='proxy_upload'),
    url('^proxy/change/$', views.proxy_change, name='proxy_change'),
    url('^proxy/check/$', views.proxy_check, name='proxy_check'),
    url('^spider/view/$', views.spider_view, name='spider_view'),
    url('^spider/run/$', views.spider_run, name='spider_run'),
]
