from django.core.cache import cache
from django.db import models


class Backend(models.Model):
    """
    This is a model of our backend. It only has 2 properties for testing purposes but this can be extended.
    name: name of the ad backend service
    is_active: declares whether it should be used or not
    """
    name = models.CharField(max_length=120)
    order = models.IntegerField(default=9999)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        cache.delete_pattern('*backends*')
        super().save(args, kwargs)

