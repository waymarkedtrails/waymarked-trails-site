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
from routemap.skating.models import SkatingRoutes

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

mapinfo = {
    'manager' : SkatingRoutes.objects,
    'title': 'Inline Skating',
    'cssfile' : 'skating_theme.css',
    'bgimage' : 'banner_skating.jpg',
    'tileurl' : 'http://tile.sihtu/skating'
}

urlpatterns = patterns('routemap.views.mapview',
    (r'^$', 'route_map_view', mapinfo, 'simplemap'),
    (r'^relation/(?P<relid>\d+)$', 'route_map_view', mapinfo, 'relationmap'),
    (r'^route/(?P<name>.+)$', 'route_map_view', mapinfo, 'routemap'),
)

routeinfo = {
    'manager' : SkatingRoutes.objects
}

listinfo = {
    'manager' : SkatingRoutes.objects,
    'hierarchytab' : 'skating.hierarchy',
    'segmenttab' : 'skating.segments'
}

urlpatterns += patterns('routemap.views.routeinfo',
    (r'^routebrowser/(?P<route_id>\d+)/info$', 'info', routeinfo, 'route_info'),
    (r'^routebrowser/(?P<route_id>\d+)/gpx$', 'gpx', routeinfo, 'route_gpx'),
    (r'^routebrowser/(?P<route_id>\d+)/json$', 'json', routeinfo, 'route_json'),
    (r'^routebrowser/$', 'list', listinfo, 'route_list')
)

helppageinfo = {
    'sources' : (settings._BASEDIR + 'helppages/skating_about',
                settings._BASEDIR + 'helppages/maps_disclaimers',
                ),
    'pagetitle': 'Inline Skating',
    'cssfile' : 'skating_theme.css',
    'bgimage' : 'banner_skating.jpg'
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
