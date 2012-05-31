from django.db import models
from django.contrib.contenttypes import generic

from cms.models.pagemodel import Page
from cms.models.pluginmodel import CMSPlugin

from uploadit.models import UploadedFile


class CMSMediaGallery(models.Model):
    name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=150, primary_key=True)
    # Neccessary for django-uploadit
    created_on = models.DateTimeField(auto_now_add=True)
    # Associates a this gallery to a cms page
    cms_page = models.OneToOneField(Page, editable=False, related_name="cms_media_gallery")
    pictures = generic.GenericRelation(UploadedFile, content_type_field='parent_type', object_id_field='parent_id')
    
    @property
    def get_pictures(self):
        return self.pictures.all()


    def __unicode__(self):
        return ''.join([self.cms_page.get_title(), self.name])