from django.db import models
from localflavor.us.us_states import STATE_CHOICES
from localflavor.us.models import USStateField
from django_google_maps import fields as map_fields



#Consider implementing something like http://www.yetihq.com/blog/integrating-google-places-api-and-django-tastypie/ to directly call google places into Pool objects


class Pool(models.Model):
    name = models.CharField(max_length=300)
    address = map_fields.AddressField(max_length=800)
    geolocation = map_fields.GeoLocationField(blank=True)
    rating = models.FloatField(default=0)

    def __str__(self):
        return "%s at %s" % (self.name,  self.address)

