# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2011-2012 Sarah Hoffmann
#               2012-2013 Michael Spreng
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
from django.conf import settings

urlpatterns = patterns('routemap.apps.slopeinfo.views',
    url(r'^(?P<route_id>[rwv]\d+)/info$', 'info', name='info'),
    url(r'^(?P<route_id>[rwv]\d+)/gpx$', 'gpx', name='gpx'),
    url(r'^(?P<route_id>[rwv]\d+)/json$', 'json', name='json'),
    url(r'^(?P<route_id>[rwv]\d+)/wikilink$', 'wikilink', name='wikilink'),
    url(r'^jsonbox$', 'json_box', name='jsonbox'),
)

if settings.SHOW_ELEV_PROFILE:
    urlpatterns += patterns('routemap.apps.slopeinfo.elevationprofile',
        url(r'^(?P<route_id>\d+)/profile/json$', 'elevation_profile_json', name='profile_json')
    )

urlpatterns += patterns('routemap.apps.slopeinfo.views',
    url(r'^$', 'list', name='list')
)

