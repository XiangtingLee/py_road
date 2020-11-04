from django.conf.urls import url
from . import views

app_name = "user"

urlpatterns = [
    url('^manage/$', views.manage_view, name='manage_view'),
    url('^manage/filter/$', views.manage_filter, name='manage_filter'),
    url('^manage/profile/(?P<uid>[0-9]+)/$', views.manage_profile, name='manage_profile'),
    url('^profile/$', views.profile_view, name='profile_view'),
    url('^profile/upload/$', views.profile_upload, name='profile_upload'),
    url('^profile/update/$', views.profile_update, name='profile_update'),
    url('^password/$', views.password_view, name='password_view'),
    url('^password/change/$', views.password_change, name='password_change'),
]