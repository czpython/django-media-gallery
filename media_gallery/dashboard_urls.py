from django.conf.urls.defaults import *


urlpatterns = patterns('media_gallery.views',
	url(r'^media-gallery/dashboard/$', 'dashboard', name="gallery-dashboard"),
    url(r'^media-gallery/create/$', 'create_gallery', name="gallery-create"),
    url(r'^media-gallery/(?P<slug>[-\w]+)/edit/$', 'edit_gallery', name="gallery-edit"),
    url(r'^media-gallery/(?P<slug>[-\w]+)/upload/$', 'upload_images', name="gallery-upload-images"),
    url(r'^media-gallery/(?P<slug>[-\w]+)/delete/$', 'delete_gallery', name="gallery-delete"),
    url(r'^media-gallery/(?P<slug>[-\w]+)/image/(?P<img>\d+)/delete/$', 'delete_image', name="gallery-delete-image"),
    url(r'^media-gallery/(?P<slug>[-\w]+)/publish/$', 'publish_gallery', name="gallery-publish"),
)