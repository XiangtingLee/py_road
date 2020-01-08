app_name = 'position'

from django.conf.urls import url
from . import views

urlpatterns = [
    url('^display/view/$', views.display_view, name='display_view'),
    url('^display/filter/$', views.display_filter, name='display_filter'),
    url('^visualization/view/$', views.visualization_view, name='visualization_view'),
    url('^visualization/data/$', views.visualization_data, name='visualization_data'),
    url('^cleaning/view/$', views.cleaning_view, name='cleaning_view'),
    url('^cleaning/check/$', views.cleaning_check, name='cleaning_check'),
]