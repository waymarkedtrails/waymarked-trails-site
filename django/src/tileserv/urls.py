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

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from tileserv.models import TileModel

urlpatterns = []
tilepat = r'%s/(?P<zoom>\d+)/(?P<tilex>\d+)/(?P<tiley>\d+).png'
image_data = open(settings.EMPTY_TILE, "rb").read()

for tab in settings.TILE_TABLES:
    # create a new class
    class Meta:
        pass
    setattr(Meta, 'db_table', tab)
    tabmodel = type('Model' + tab, (TileModel, ), 
                    {'__module__' : 'tileserv.models',
                     'Meta' : Meta })
    urlpatterns += patterns('tileserv.views',
            (tilepat % tab, 'png_tile', { 'table' : tabmodel,
                                          'empty' : image_data})
    )
