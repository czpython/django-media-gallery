from cms_media_gallery.models import Collection

from ajax_select import LookupChannel


class PageLookup(LookupChannel):

    model = Collection

    def get_query(self, q, request):
        return Collection.objects.filter(name__icontains=q).order_by('name')

