from django.conf.urls import url
from . import views

app_name = 'log'

urlpatterns = [
    url('^spider/$', views.log_spider, name='log_spider'),
]
