app_name = 'position'

from django.conf.urls import url
from . import views

urlpatterns = [
    url('^reveal/view/$', views.reveal_view, name='reveal_view'),
    url('^reveal/filter/$', views.reveal_filter, name='reveal_filter'),
    url('^visualization/view/$', views.visualization_view, name='visualization_view'),
    url('^visualization/data/$', views.visualization_data, name='visualization_data'),
]