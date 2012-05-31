from django.conf.urls.defaults import *


urlpatterns = patterns('cms_media_gallery.views',
    url(r'^gallery/create/$', 'create_gallery', name="gallery-create"),
    url(r'^gallery/(?P<slug>[-\w]+)/edit/$', 'edit_gallery', name="gallery-edit"),
    url(r'^gallery/(?P<slug>[-\w]+)/upload/$', 'upload_images', name="gallery-upload-images"),
    url(r'^gallery/(?P<slug>[-\w]+)/image/(?P<img>\d+)/delete/$', 'delete_image', name="gallery-delete-image"),
    url(r'^gallery/(?P<slug>[-\w]+)/publish/$', 'publish_gallery', name="gallery-publish"),
)