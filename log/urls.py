app_name = 'log'

from django.conf.urls import url
from . import views

urlpatterns = [
    url('^spider/$', views.log_spider, name='log_spider'),
]