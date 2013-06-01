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

from django.conf.urls import patterns, url, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings

urlpatterns = i18n_patterns('',
        (r'^search/', include('routemap.apps.search.urls', namespace='search')),
        (r'^routebrowser/', include('routemap.apps.routeinfo.urls', namespace='route')),
        (r'^segments/', include('routemap.apps.segments.urls', namespace='segment')),
        (r'^help/', include('routemap.apps.helppages.urls')),
)

urlpatterns += patterns('',
        (r'^i18n/', include('django.conf.urls.i18n')),
)

# for development
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT})
)


urlpatterns += i18n_patterns('',
        (r'^', include('routemap.apps.map.urls')),
)
