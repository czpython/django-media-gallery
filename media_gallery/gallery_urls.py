from django.conf.urls.defaults import *


urlpatterns = patterns('media_gallery.views',
	url(r'^(?P<collection>[-\w]+)/$', 'view_galleries', name="media-gallery-galleries)"),
    url(r'^(?P<collection>[-\w]+)/(?P<gallery>[-\w]+)/$', 'view_gallery', name="media-gallery"),
)