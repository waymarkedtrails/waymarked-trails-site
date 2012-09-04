#!/usr/bin/python
# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2011-2012 Sarah Hoffmann
#
# This is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from django.conf.urls.defaults import *
from django.conf import settings
from routemap.mtbmap.models import MtbRoutes

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

handler404 = 'routemap.views.error.handler404'
handler500 = 'routemap.views.error.handler500'

mapinfo = {
    'manager' : MtbRoutes.objects,
    'tileurl' : settings.ROUTEMAP_TILE_URL
}

urlpatterns = patterns('routemap.views.mapview',
    (r'^$', 'route_map_view', mapinfo, 'simplemap'),
    (r'^relation/(?P<relid>\d+)$', 'route_map_view', mapinfo, 'relationmap'),
    (r'^route/(?P<name>.+)$', 'route_map_view', mapinfo, 'routemap'),
)

routeinfo = {
    'manager' : MtbRoutes.objects
}

listinfo = {
    'manager' : MtbRoutes.objects,
    'hierarchytab' : 'mtbmap.hierarchy',
    'segmenttab' : 'mtbmap.segments'
}

urlpatterns += patterns('routemap.views.routeinfo',
    (r'^routebrowser/(?P<route_id>\d+)/info$', 'info', routeinfo, 'route_info'),
    (r'^routebrowser/(?P<route_id>\d+)/gpx$', 'gpx', routeinfo, 'route_gpx'),
    (r'^routebrowser/(?P<route_id>\d+)/json$', 'json', routeinfo, 'route_json'),
    (r'^routebrowser/(?P<route_id>\d+)/wikilink$', 'wikilink', routeinfo, 'route_wikilink'),
    (r'^routebrowser/jsonbox$', 'json_box', routeinfo, 'route_jsonbox'),
    (r'^routebrowser/$', 'list', listinfo, 'route_list')
)

urlpatterns += patterns('routemap.views.elevationprofile',
    (r'^routebrowser/(?P<route_id>\d+)/profile/png$', 'elevation_profile_png', routeinfo, 'route_profile_png'),
    (r'^routebrowser/(?P<route_id>\d+)/profile/json$', 'elevation_profile_json', routeinfo, 'route_profile_json')
)

urlpatterns += patterns('routemap.views.search',
    (r'^search/nominatim$', 'place_search', routeinfo, 'place_search'),
    (r'^search/$', 'search', routeinfo, 'search'),
)

urlpatterns += patterns('routemap.views.helppages',
    (r'^help/(?P<page>[\w/]+)$', 'helppage_view', settings.ROUTEMAP_HELPPAGES, 'helppage'),
        
)

# for development
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT})
)
