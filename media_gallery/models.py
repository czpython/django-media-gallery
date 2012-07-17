import random

from django.db import models
from django.contrib.contenttypes import generic
from  django.conf import settings

from uploadit.models import FileGroup

from pwd_this.models import Password


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
    lock = models.BooleanField(default=False, verbose_name='login Required', 
        help_text="Prompts for a password when viewing this gallery.")
    password = models.OneToOneField(Password, related_name='media_gallery', editable=False, blank=True, null=True)
    published = models.BooleanField(default=False)
    pictures = models.ForeignKey(FileGroup, null=True, blank=True)

    @property
    def thumbail(self):
        """
            Gets a random picture from this gallery and returns it.
        """
        try:
            return self._thumbail
        except AttributeError:
            if self.pictures is not None:
                self._thumbail = random.choice(self.pictures.get_files())
                return self._thumbail

    def get_picture_positions(self):
        pictures = self.pictures.get_files()
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