app_name = 'position'

from django.conf.urls import url
from . import views

urlpatterns = [
    url('^visualization/view/$', views.visualization_view, name='visualization_view'),


    url('^visualization/data/$', views.visualization_data, name='visualization_data'),
]