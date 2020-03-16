from django.conf.urls import url
from . import views

app_name = "wuhan2020"

urlpatterns = [
    url('^visualization/back.svg$', views.back_svg, name='visualization_view'),
    url('^visualization/view/$', views.visualization_view, name='visualization_view'),
    url('^visualization/data/$', views.visualization_data, name='visualization_data'),
    url('^visualization/conversion/data/$', views.visualization_conversion_data, name='visualization_conversion_data'),
    url('^timeline/view/$', views.timeline_view, name='timeline_view'),
    url('^timeline/data/$', views.timeline_data, name='timeline_data'),
]
