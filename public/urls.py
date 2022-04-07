from django.conf.urls import url
from . import views

app_name = 'public'

urlpatterns = [
    url('^proxy/$', views.proxy_view, name='proxy_view'),
    url('^proxy/filter/$', views.proxy_filter, name='proxy_filter'),
    url('^proxy/upload/$', views.proxy_upload, name='proxy_upload'),
    url('^proxy/change/$', views.proxy_change, name='proxy_change'),
    url('^proxy/check/$', views.proxy_check, name='proxy_check'),

    url('^spider/manage/view/$', views.spider_manage_view, name='spider_manage_view'),
    url('^spider/manage/data/$', views.spider_manage_data, name='spider_manage_data'),
    url('^spider/manage/probe/$', views.spider_manage_probe, name='spider_manage_probe'),
    url('^spider/manage/edit/(?P<spider_id>[0-9]+)/$', views.spider_manage_edit, name='spider_manage_edit'),
    url('^spider/manage/show/(?P<spider_id>[0-9]+)/$', views.spider_manage_show, name='spider_manage_show'),
    url('^spider/component/view/$', views.spider_component_view, name='spider_component_view'),
    url('^spider/component/data/$', views.spider_component_data, name='spider_component_data'),
    url('^spider/component/edit/(?P<component_id>[0-9]+)/$', views.SpiderComponentEdit.as_view(), name='spider_component_edit'),
    url('^spider/component/show/(?P<component_id>[0-9]+)/$', views.spider_component_show, name='spider_component_show'),
    url('^spider/operate/view/$', views.spider_operate_view, name='spider_operate_view'),
    url('^spider/operate/run/$', views.spider_operate_run, name='spider_operate_run'),
    url('^spider/operate/run/frame/$', views.spider_operate_run_frame, name='spider_operate_run_frame'),

    url('^administrativeDiv/$', views.administrative_div_view, name='administrative_div_view'),
    url('^administrativeDiv/filter/$', views.administrative_div_filter, name='administrative_div_filter'),
    url('^administrativeDiv/edit/(?P<div_id>[0-9]+)/$', views.administrative_div_edit, name='administrative_div_edit'),
]
