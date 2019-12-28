app_name = 'position'

from django.conf.urls import url
from . import views

urlpatterns = [
    url('^visualization/view/$', views.visualization_view, name='visualization_view'),


    url('^tag_analysis/$', views.tag_analysis, name='tag_analysis'),
]