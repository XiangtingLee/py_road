from django.conf.urls import url
from . import views

app_name = 'log'

urlpatterns = [
    url('^spider/filter/$', views.spider_filter, name='spider_filter'),
]
