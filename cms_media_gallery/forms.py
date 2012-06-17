from django import forms
from django.template.defaultfilters import slugify

from ajax_select.fields import AutoCompleteField

from cms_media_gallery.models import Collection, MediaGallery



class GalleryForm(forms.ModelForm):

    collection  = AutoCompleteField('media_gallery_collection', label='Client')
    password = forms.CharField(max_length='120', required=False, help_text='Password to be used by user to access this gallery.')

    def __init__(self, *args, **kwargs):
        if 'edit' in kwargs:
            edit = kwargs.pop('edit')
        else:
            edit = False
        super(GalleryForm, self).__init__(*args, **kwargs)
        if edit is False:
            self.fields['published'].widget = forms.HiddenInput()
            self.fields['password'].widget = forms.HiddenInput()
            self.fields['lock'].widget = forms.HiddenInput()


    def clean_collection(self):
        collection = self.cleaned_data['collection']
        slug = slugify(collection)
        try:
            collection = Collection.objects.get(pk=slug)
        except Collection.DoesNotExist:
            collection = Collection.objects.create(pk=slug, name=collection)
        return collection

    def clean(self):
        """
            Validates if require_password is True then user should have submitted password.
        """
        cleaned_data = super(GalleryForm, self).clean()
        require_password = cleaned_data.get('lock')
        password = cleaned_data.get('password')
        if require_password is True and not password:
            self._errors["password"] = self.error_class(['Please enter a password.'])
            del cleaned_data['password']
        return cleaned_data

    class Meta:
        model = MediaGallery
        fields = ('name', 'slug', 'published', 'collection', 'lock', 'password')
        widgets = {
            'name': forms.TextInput(attrs={'class':'input-large'}),
            'slug': forms.TextInput(attrs={'class':'input-large'}),
        }
