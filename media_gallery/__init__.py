from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    UPLOADIT_FILE_MODEL = settings.UPLOADIT_FILE_MODEL
except AttributeError, e:
    raise ImproperlyConfigured('Please add UPLOADIT_FILE_MODEL = "media_gallery.models.UploadedImage" to your settings file.')

try:
    UPLOADIT_PROCESS_FILE = settings.UPLOADIT_PROCESS_FILE
except AttributeError, e:
    raise ImproperlyConfigured('Please add UPLOADIT_PROCESS_FILE = "media_gallery.models.process_image" to your settings file.')
