import random

from django.db import models
from django.contrib.contenttypes import generic

from cms.models.pagemodel import Page
from cms.models.pluginmodel import CMSPlugin

from uploadit.models import UploadedFile

from cms_media_gallery.managers import CMSMediaGalleryManager


class CMSMediaGallery(models.Model):
    name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=150, primary_key=True)
    # Neccessary for django-uploadit
    created_on = models.DateTimeField(auto_now_add=True)
    # Associates a this gallery to a cms page
    cms_page = models.OneToOneField(Page, editable=False, related_name="cms_media_gallery")
    pictures = generic.GenericRelation(UploadedFile, content_type_field='parent_type', object_id_field='parent_id')
    objects = CMSMediaGalleryManager()

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