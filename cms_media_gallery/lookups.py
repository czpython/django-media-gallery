from django.utils.html import escape
from django.db.models import Q
from django.conf import settings

from cms.models.pagemodel import Page

from ajax_select import LookupChannel

CMS_MEDIA_GALLERY_PAGE = settings.CMS_MEDIA_GALLERY_PAGE


class PageLookup(LookupChannel):

    model = Page

    def get_query(self, q, request):
        return Page.objects.filter(parent__reverse_id=CMS_MEDIA_GALLERY_PAGE).filter(title_set__title__icontains=q).order_by('title_set__title')

