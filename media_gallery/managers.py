from django.db import models

class MediaGalleryManager(models.Manager):
	"""
		Default manager wrapper for MediaGallery.
	"""

	def with_images(self):
		# I call distinct because for some reason django is returning multiple instances per result.
		return self.get_query_set().filter(images__isnull=False).distinct()