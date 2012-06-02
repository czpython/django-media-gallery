import base64

from django.conf import settings

from cms.api import create_page, publish_page
from cms.models.pagemodel import Page



def encode_string(string):
    """
        Encrypts the string.
    """
    return base64.b64encode(string)


def decode_string(string):
    return base64.b64decode(string)


def get_or_create_page(parent, child, template):
    if isinstance(parent, dict):
        parent = Page.objects.get(**parent)
    try:
        page = parent.children.get(title_set__title=child)
    except parent.children.model.DoesNotExist:
        # Create the parent page if it doesn't exist
        page = create_page(title=child, 
            template=template, 
            language='en', 
            parent=parent)
    return page


def cms_recursive_publish(page, user):
    """
        Small wrapper of django-cms publish.
    """
    if not page.published:
        publish_page(page, user, approve=True)
    if page.parent:
        return cms_recursive_publish(page.parent, user)