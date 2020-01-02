app_name = "user"

from django.conf.urls import url
from . import views

urlpatterns = [
    url('^info/view/$', views.info_view, name='info_view'),
    url('^info/upload/$', views.info_upload, name='info_upload'),
    url('^info/change/$', views.info_change, name='info_change'),
]