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

from django.conf.urls import patterns, url

urlpatterns = patterns('routemap.apps.map.views',
    url(r'^$', 'route_map_view', name='simplemap'),
    url(r'^relation/(?P<routeid>\d+)$', 'route_map_view', {'osm_type' : 'relation'}, name='relationmap'),
    url(r'^way/(?P<routeid>\d+)$', 'route_map_view', {'osm_type' : 'way'}, name='waymap'),
    url(r'^route/(?P<name>.+)$', 'route_map_view', name='routemap'),
)

