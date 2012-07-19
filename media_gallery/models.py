import random

from django.db import models
from django.conf import settings

from pwd_this.models import Password



class Collection(models.Model):
    """
        A collection of galleries.
    """
    name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=150, primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name


class MediaGallery(models.Model):
    name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=150, primary_key=True)
    # Neccessary for django-uploadit
    created_on = models.DateTimeField(auto_now_add=True)
    collection = models.ForeignKey(Collection, related_name='gallery_set')
    lock = models.BooleanField(default=False, verbose_name='login Required', 
        help_text="Prompts for a password when viewing this gallery.")
    password = models.OneToOneField(Password, related_name='media_gallery', editable=False, blank=True, null=True)
    published = models.BooleanField(default=False)

    @property
    def thumbnail(self):
        """
            Gets a random image from this gallery and returns its thumbnail.
        """
        try:
            return self._thumbnail
        except AttributeError:
            if self.images is not None:
                self._thumbnail = random.choice(self.images.all()).thumbnail
                return self._thumbnail

    def get_picture_positions(self):
        """
            Returns a dictionary mapping an image's position with its id.
        """
        pictures = self.images.get_custom_sorted()
        positions = {}
        for pos, picture in enumerate(pictures):
            # 1 indexed
            positions[picture.id] = pos + 1
        return positions

    @models.permalink
    def get_absolute_url(self):
        return ('media-gallery', [self.collection.slug, self.slug])


    def __unicode__(self):
        return self.name


def calc_image_path(instance, name):
    return "%s/%s" % (instance.gallery.name, name)


def calc_thumbnail_path(instance, name):
    return "%s/thumbnails/%s" % (instance.gallery.name, name)


class UploadedImage(models.Model):
    """
        Extends the UploadedFile object.
        Adds a relationship to MediaGallery.
    """
    image = models.ImageField(upload_to=calc_image_path)
    thumbnail = models.ImageField(upload_to=calc_thumbnail_path)
    gallery = models.ForeignKey(MediaGallery, related_name='images')
    upload_date = models.DateTimeField(auto_now_add=True)


    def __unicode__(self):
        return self.image.name

    class Meta:
        # Defined as abstract because this is not meant to create a table.
        # But to extend the UploadedFile model which is in charge of creating its table.
        abstract = True
