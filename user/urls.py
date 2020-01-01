app_name = "user"

from django.conf.urls import url
from . import views

urlpatterns = [
    url('^info/view/$', views.info_view, name='info_view'),
]