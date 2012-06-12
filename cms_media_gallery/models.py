import random

from django.db import models
from django.contrib.contenttypes import generic

from uploadit.models import UploadedFile

from cms_media_gallery.managers import MediaGalleryManager

class PasswordProtect(models.Model):
    name = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=85)

    def __unicode__(self):
        return self.name

class Collection(models.Model):
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
    protect = models.OneToOneField(PasswordProtect, related_name='media_gallery', blank=True, null=True)
    published = models.BooleanField(default=False)
    pictures = generic.GenericRelation(UploadedFile, content_type_field='parent_type', object_id_field='parent_id')
    objects = MediaGalleryManager()

    @property
    def get_pictures(self):
        return self.pictures.all()

    @property
    def thumbail(self):
        """
            Gets a random picture from this gallery and returns it.
        """
        try:
            return self._thumbail
        except AttributeError:
            if self.pictures is not None:
                self._thumbail = random.choice(self.pictures.all())
                return self._thumbail

    def get_picture_positions(self):
        pictures = self.pictures.all().order_by('id')
        positions = {}
        for pos, picture in enumerate(pictures):
            # 1 indexed
            positions[picture.id] = pos + 1
        return positions



    def __unicode__(self):
        return self.name