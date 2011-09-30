from django.conf.urls.defaults import *
from django.conf import settings
from routemap.cycling.models import CyclingRoutes

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

mapinfo = {
    'template' : 'cycling/basemap.html',
    'manager' : CyclingRoutes.objects
}

urlpatterns = patterns('routemap.views.mapview',
    (r'^$', 'route_map_view', mapinfo, 'simplemap'),
    (r'^relation/(?P<relid>\d+)$', 'route_map_view', mapinfo, 'relationmap'),
    (r'^route/(?P<name>.+)$', 'route_map_view', mapinfo, 'routemap'),
)

routeinfo = {
    'manager' : CyclingRoutes.objects
}

listinfo = {
    'manager' : CyclingRoutes.objects,
    'hierarchytab' : 'cycling.hierarchy',
    'segmenttab' : 'cycling.segments'
}

urlpatterns += patterns('routemap.views.routeinfo',
    (r'^routebrowser/(?P<route_id>\d+)/info$', 'info', routeinfo, 'route_info'),
    (r'^routebrowser/(?P<route_id>\d+)/gpx$', 'gpx', routeinfo, 'route_gpx'),
    (r'^routebrowser/(?P<route_id>\d+)/json$', 'json', routeinfo, 'route_json'),
    (r'^routebrowser/$', 'list', listinfo, 'route_list')
)

helppageinfo = {
    'source' : settings._BASEDIR + 'helppages/cycling_about',
    'template' : 'cycling/docpage.html'
}

urlpatterns += patterns('routemap.views.helppages',
    ('osmc_symbol_legende', 'osmc_symbol_legende'),
    (r'^(?P<page>[\w/]+)$', 'helppage_view', helppageinfo, 'helppage'),
        
)

# for development
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT})
)
