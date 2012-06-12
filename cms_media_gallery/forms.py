from django import forms
from django.template.defaultfilters import slugify

from ajax_select.fields import AutoCompleteField

from cms_media_gallery.models import Collection, MediaGallery

class GalleryForm(forms.ModelForm):

    collection  = AutoCompleteField('media_gallery_collection', label='Client')

    def __init__(self, *args, **kwargs):
        if 'edit' in kwargs:
            edit = kwargs.pop('edit')
        else:
            edit = False
        super(GalleryForm, self).__init__(*args, **kwargs)
        if edit is False:
            self.fields['published'].widget = forms.HiddenInput()

    def clean_collection(self):
        collection = self.cleaned_data['collection']
        slug = slugify(collection)
        try:
            collection = Collection.objects.get(pk=slug, name=collection)
        except Collection.DoesNotExist:
            collection = Collection.objects.create(pk=slug)
        return collection


    class Meta:
        model = MediaGallery
        widgets = {
            'name': forms.TextInput(attrs={'class':'input-large'}),
            'slug': forms.TextInput(attrs={'class':'input-large'}),
        }
        exclude = ('protect')