app_name = "wuhan2020"

from django.conf.urls import url
from . import views

urlpatterns = [
    url('^visualization/view/$', views.visualization_view, name='visualization_view'),
    url('^visualization/data/$', views.visualization_data, name='visualization_data'),
    url('^timeline/view/$', views.timeline_view, name='timeline_view'),
    url('^timeline/data/$', views.timeline_data, name='timeline_data'),
]