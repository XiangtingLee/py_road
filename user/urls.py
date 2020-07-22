from django.conf.urls import url
from . import views

app_name = "user"

urlpatterns = [
    url('^manage/$', views.manage_view, name='manage_view'),
    url('^manage/filter/$', views.manage_filter, name='manage_filter'),
    url('^manage/edit/(?P<uid>[0-9]+)/$', views.manage_edit, name='manage_edit'),
    url('^info/view/$', views.info_view, name='info_view'),
    url('^info/upload/$', views.info_upload, name='info_upload'),
    url('^info/change/$', views.info_change, name='info_change'),
    url('^password/view/$', views.password_view, name='password_view'),
    url('^password/change/$', views.password_change, name='password_change'),
]