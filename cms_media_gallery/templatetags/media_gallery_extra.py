import os

from django import template


register = template.Library()


# Thanks to rz. http://stackoverflow.com/a/4046508/389453
@register.filter
def filename(value):
    return os.path.basename(value.name)