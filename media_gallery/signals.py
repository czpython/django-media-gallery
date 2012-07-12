from django.dispatch import Signal



media_gallery_created = Signal(providing_args=["gallery"])