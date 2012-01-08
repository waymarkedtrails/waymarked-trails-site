#!/usr/bin/python
# This file is part of Lonvia's Route Maps Project
# Copyright (C) 2011 Sarah Hoffmann
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
from routemap.cycling.models import CyclingRoutes

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

mapinfo = {
    'manager' : CyclingRoutes.objects,
    'tileurl' : 'http://tile.sihtu/cycling'
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

urlpatterns += patterns('routemap.views.search',
    (r'^search/nominatim$', 'place_search', routeinfo, 'place_search'),
    (r'^search/$', 'search', routeinfo, 'search'),
)

helppageinfo = {
    'sources' : (settings._BASEDIR + 'helppages/cycling_about',
                settings._BASEDIR + 'helppages/maps_disclaimers',
                ),
}

urlpatterns += patterns('routemap.views.helppages',
    ('osmc_symbol_legende', 'osmc_symbol_legende'),
    (r'^help/(?P<page>[\w/]+)$', 'helppage_view', helppageinfo, 'helppage'),
        
)

# for development
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT})
)
