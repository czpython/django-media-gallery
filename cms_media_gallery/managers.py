from django.db import models

class CMSMediaGalleryManager(models.Manager):
	"""
		Default manager wrapper for CMSMediaGallery.
	"""

	def with_images(self):
		# I call distinct because for some reason django is returning multiple instances per result.
		return self.get_query_set().filter(pictures__isnull=False).distinct()