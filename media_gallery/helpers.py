from PIL import Image
import StringIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File

from media_gallery.models import MediaGallery



def create_thumbnail(fullsizeimg, maxwidth, maxheight):
    """
        Creates a thumbnail from fullsizeimg.
        Borrowed from http://blog.lagentz.com/python/automatic-image-resizing-and-cropping-with-pylons/
    """

    ratio = 1. * maxwidth / maxheight

    im = Image.open(fullsizeimg)
    (width, height) = im.size        # get the size of the input image
    if width > height * ratio:
        # crop the image on the left and right side
        newwidth = int(height * ratio)
        left = width / 2 - newwidth / 2
        right = left + newwidth
        # keep the height of the image
        top = 0
        bottom = height
    elif width < height * ratio:
        # crop the image on the top and bottom
        newheight = int(width * ratio)
        top = height / 2 - newheight / 2
        bottom = top + newheight
        # keep the width of the impage
        left = 0
        right = width
    if width != height * ratio:
        im = im.crop((left, top, right, bottom))
    im = im.resize((maxwidth, maxheight), Image.ANTIALIAS)
    return im

def process_image(**kwargs):
    """
        Creates an Image and assigns it to kwargs['gallery'].
        @kwargs['gallery'] - Slug of the gallery for this image.
        @kwargs['filepath'] - Path to the Image File.
        @kwargs['filename'] - Name of the Image File.
    """

    gallery = kwargs.get('gallery')
    filepath, filename = kwargs.get('filepath'), kwargs.get('filename')

    try:
        gallery = MediaGallery.objects.get(pk__exact=gallery)
    except MediaGallery.DoesNotExist:
        raise
    with open(filepath) as image:
        thumb = create_thumbnail(image, 200, 200)
        thumb_io = StringIO.StringIO()
        thumb.save(thumb_io, format='JPEG')
        thumbnail = InMemoryUploadedFile(thumb_io, None, filename, 'image/jpeg', thumb_io.len, None)
        gallery.images.create(image=File(image, name=filename), thumbnail=thumbnail, gallery=gallery)
    return
