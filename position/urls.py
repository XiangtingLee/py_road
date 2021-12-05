from django.conf.urls import url
from . import views

app_name = 'position'


urlpatterns = [
    url('^display/view/$', views.display_view, name='display_view'),
    url('^display/node/data/$', views.node_data, name='node_data'),
    url('^display/filter/$', views.display_filter, name='display_filter'),
    url('^visualization/view/$', views.visualization_view, name='visualization_view'),
    url('^cleaning/view/$', views.cleaning_view, name='cleaning_view'),
    url('^cleaning/filter/$', views.cleaning_filter, name='cleaning_filter'),
    url('^cleaning/check/$', views.cleaning_check, name='cleaning_check'),
]
