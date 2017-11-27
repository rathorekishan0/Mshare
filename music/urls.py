from django.conf.urls import url
from . import views
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView,LogoutView
app_name='music'
urlpatterns = [
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^following/$', views.following.as_view(), name='following'),
    url(r'^follower/$', views.follower.as_view(), name='follower'),
    url(r'^profilecreate/(?P<pk>[0-9]+)/$', views.profilecreate.as_view(), name='profilecreate'),
    url(r'^songplay/(?P<pk>[0-9]+)/$', views.songplay.as_view(), name='songplay'),
    url(r'^myfav/$', views.myfav.as_view(), name='myfav'),
    url(r'^$',views.indexpage,name='indexpage'),
    url(r'^search/$', views.searchview.as_view(), name='search'),
    url(r'^song-like/$', views.liketoggle.as_view(), name='like'),
    url(r'^home-feed/$', views.homeview.as_view(), name='homefeed'),
    url(r'^welcome/$', views.welcome.as_view(), name='welcome'),
    url(r'^navbar/$', TemplateView.as_view(template_name='music/navbar.html'), name='navbar'),
    url(r'^activation/$', TemplateView.as_view(template_name='music/activation.html'), name='activation'),
    url(r'^activate/(?P<code>[a-z0-9].*)/$', views.activate_user_view, name='activate'),
    url(r'^register/$', views.registerview.as_view(), name='register'),
    url(r'^profile-follow/$', views.profilefollowtoggle.as_view(), name='follow'),
    url(r'^createmusic/$', views.createmusic.as_view(), name='createmusic'),
    url(r'^login/$',LoginView.as_view(),name ='login'),
    url(r'^(?P<slug>[\w-]+)/$', views.profiledetail.as_view(), name='profiledetail'),

    # url(r'^(?P<pk>[0-9]+)/$', views.detailview.as_view(), name='detail'),
    # url(r'album/add/$',views.albumcreate.as_view(),name='album-add'),
    # url(r'album/(?P<pk>[0-9]+)/$', views.albumupdate.as_view(), name='album-update'),
    # url(r'album/(?P<pk>[0-9]+)/delete/$', views.albumdelete.as_view(), name='album-delete'),

]