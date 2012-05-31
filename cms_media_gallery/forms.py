from django import forms
from django.conf import settings

from cms.api import create_page

from ajax_select.fields import AutoCompleteField

from cms_media_gallery.models import CMSMediaGallery

class GalleryForm(forms.ModelForm):

    parent  = AutoCompleteField('cms_media_gallery_page', label='Client')

    def __init__(self, *args, **kwargs):
        if 'edit' in kwargs:
            edit = kwargs.pop('edit')
        else:
            edit = False
        super(GalleryForm, self).__init__(*args, **kwargs)
        if edit:
            self.fields['publish'] = forms.BooleanField(initial=False)

    class Meta:
        model = CMSMediaGallery
        widgets = {
            'name': forms.TextInput(attrs={'class':'input-large'}),
            'slug': forms.TextInput(attrs={'class':'input-large'}),
        }