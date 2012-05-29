from django import forms

from models import Gallery


class GalleryForm(forms.ModelForm):
	class Meta:
		model = Gallery
		widgets = {
            'name': forms.TextInput(attrs={'class':'input-large'}),
            'slug': forms.TextInput(attrs={'class':'input-large'})
        }