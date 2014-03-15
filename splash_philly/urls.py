from django.conf.urls import patterns, include, url
from splash_philly import views,settings
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'splash_philly.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^places/$', views.PlacesView.as_view(), name='places'),
    url(r'^add_places/$', views.AddPlacesToDatabaseView.as_view(), name='places_add'),
    url(r'^map$', views.MapView.as_view(),name='map'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
)

