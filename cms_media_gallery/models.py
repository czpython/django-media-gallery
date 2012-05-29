from django.db import models
from django.contrib.contenttypes import generic

from uploadit.models import UploadedFile


class Gallery(models.Model):
    name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=150, primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    pictures = generic.GenericRelation(UploadedFile, content_type_field='parent_type', object_id_field='parent_id')
    
    @property
    def get_pictures(self):
        return self.pictures.all()

    def __unicode__(self):
        return self.name