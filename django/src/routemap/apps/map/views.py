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

from datetime import datetime
from django.utils.timezone import utc

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render

from django.conf import settings

from django.utils.importlib import import_module

table_module, table_class = settings.ROUTEMAP_ROUTE_TABLE.rsplit('.',1)
table_module = import_module(table_module)

def route_map_view(request, relid=None, name=None, template='basemap.html'):
    extent = None
    showroute = -1
    if relid is not None:
        try:
            obj = getattr(table_module, table_class).objects.get(id=relid)
            extent = obj.geom.extent
            showroute = obj.id
        except:
            showroute = relid
    elif name is not None:
        try:
            obj = getattr(table_module, table_class).objects.get(name__iexact=name)
            extent = obj.geom.extent
            showroute = obj.id
        except:
            showroute = 0

    context = {'extent' : extent,
               'showroute' : showroute,
               'tileurl' : settings.ROUTEMAP_TILE_URL
    }

    try:
        uf = open(settings.ROUTEMAP_UPDATE_TIMESTAMP)
        context['updatetime'] = datetime.strptime(uf.readline().strip(),
                                 '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=utc)
        uf.close()
    except:
        pass

    context['show_elevation_profile'] = settings.SHOW_ELEV_PROFILE

    context['ismobile'] = request.flavour == 'mobile'
    return render(request, template, context)
