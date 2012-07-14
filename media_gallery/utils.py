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
