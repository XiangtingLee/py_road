from django.conf.urls import url
from . import views

app_name = 'api'

urlpatterns = [
    url('^wechat/$', views.wechat_verify, name='wechat_verify'),
]
