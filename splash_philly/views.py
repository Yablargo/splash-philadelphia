
from django.core.exceptions import ValidationError
from django.http import request, Http404
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.views.generic import TemplateView, View,ListView,FormView
from splash_philly.models import Pool
from splash_philly import settings
from googleplaces import GooglePlaces,types,lang
import requests
from math import radians, cos, sin, asin, sqrt
"""
The home view is where we search for zip code
"""
class HomeView(TemplateView):
    template_name = 'home.html'
#    success_url = '/searchf/'

    def form_valid(self, form):
        #self.success_url = ('/search/%s/' % form.zip)
        return super(HomeView, self).form_valid(form)

"""
SearchView gives us our results...
"""
class SearchView(ListView):
    template_name = 'results.html'
    context = {'google_api_key' : settings.GOOGLE_API_KEY}



    def get_queryset(self):
        zip = self.request.GET['zip'].__str__()

        #We have a zip code, get GPS Coordinates.
        #Use google!
        #http://maps.googleapis.com/maps/api/geocode/json?address=90210&sensor=false
        #For production we'd probably pre-calculate all of the US zip codes and store, or use google entirely for gps searches.
        r = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false' % zip)
        #Get JSON
        response_json = r.json()
        #Get lat,lon from json
        lat = response_json[u'results'][0][u'geometry'][u'location'][u'lat']
        lon = response_json[u'results'][0][u'geometry'][u'location'][u'lng']

        #Ugly hack again, expensively calculate geo coords from lat,lon based on 10mi radius
        #If we were using a proper geoDB, we would just make a geo query and be done at this point, without the call to google above.

        mile_radius = 10
        #get the objects pre-sorted by rating
        pools = Pool.objects.all().order_by('-rating')
        #I've said this is ugly, right?
        matched_pools = [p for p in pools if haversine(lon, lat, p.geolocation.lon,p.geolocation.lat) < mile_radius]
        #Tell the map where to zoom.
        #self.context['lat'] = lat
        #self.context['lon'] = lon
        return matched_pools


"""Use the haversine equation to calculate distance between two points
Again, we only do this because I havent installed GeoDjango or similar!

http://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
"""
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    return value in miles
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    miles = km/1.6
    return miles

class AboutView(TemplateView):
    template_name = 'about.html'



class MapView(ListView):
    template_name = 'map.html'
    context = {'google_api_key' : settings.GOOGLE_API_KEY}
    def get_queryset(self):
        return Pool.objects.all()


class PlacesView(TemplateView):
    template_name = 'places.html'


    def get_context_data(self, **kwargs):
        context = super(PlacesView, self).get_context_data(**kwargs)
        google_places = GooglePlaces(settings.GOOGLE_API_KEY)
        query_result = google_places.nearby_search(
        location='Philadelphia, PA', keyword='Pool',
        radius=20000)

        context['places'] = query_result
        return context

class AddPlacesToDatabaseView(TemplateView):
    template_name = 'add_places.html'

    #This really should not go into the controller code here in a real app!


    def get_context_data(self, **kwargs):
        context = super(AddPlacesToDatabaseView, self).get_context_data(**kwargs)
        google_places = GooglePlaces(settings.GOOGLE_API_KEY)
        query_result = google_places.nearby_search(
        location='Philadelphia, PA', keyword='Pool',
        radius=20000)
        for place in query_result.places:
            next_result = google_places.nearby_search(
                location=place.vicinity, keyword='Pool',
                radius=20000)
            for place2 in next_result.places:
                pool2  = Pool.objects.create()
                pool2.name = place2.name
                pool2.address = place2.vicinity +" , USA" #Add this to make it work with our map db (?not sure if we need this)
                pool2.geolocation.lat = place2.geo_location['lat']
                pool2.geolocation.lon= place2.geo_location['lng']
                #I have no idea what I am doing! --MG
                if place2.rating is None:
                    pool2.rating = 0.0
                else:
                    pool2.rating = float(place2.rating)
                pool2.save()
            pool = Pool.objects.create()
            pool.name = place.name
            pool.address = place.vicinity +" , USA" #Add this to make it work with our map db (?not sure if we need this)
            pool.geolocation.lat = place.geo_location['lat']
            pool.geolocation.lon= place.geo_location['lng']
            #I have no idea what I am doing! --MG
            if place.rating is None:
                pool.rating = 0.0
            else:
                pool.rating = float(place.rating)
            pool.save()
        context['places_count'] = len(query_result.places)
        return context
