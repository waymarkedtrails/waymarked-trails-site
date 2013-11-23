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

import django.contrib.gis.geos as geos

table_modules = {}
table_classes = {}

if hasattr(settings, 'ROUTEMAP_ROUTE_TABLE'):
    table_module, table_class = settings.ROUTEMAP_ROUTE_TABLE.rsplit('.',1)
    table_module = import_module(table_module)
    table_modules['relation'] = table_module
    table_classes['relation'] = table_class

if hasattr(settings, 'ROUTEMAP_WAY_TABLE'):
    table_module, table_class = settings.ROUTEMAP_WAY_TABLE.rsplit('.',1)
    table_module = import_module(table_module)
    table_modules['way'] = table_module
    table_classes['way'] = table_class

if hasattr(settings, 'ROUTEMAP_JOINED_WAY_TABLE'):
    table_module, table_class = settings.ROUTEMAP_JOINED_WAY_TABLE.rsplit('.',1)
    table_module = import_module(table_module)
    table_modules['joined_way'] = table_module
    table_classes['joined_way'] = table_class

def route_map_view(request, routeid=None, name=None, osm_type = 'relation', template='basemap.html'):
    extent = None
    showroute = ""
    if routeid is not None:
        try:
            if osm_type == 'joined_way':
                all_ways = getattr(table_modules['joined_way'], table_classes['joined_way']).objects.filter(virtual_id=routeid)
                obj = all_ways[0]
                all_ways = [getattr(table_modules['way'], table_classes['way']).objects.get(id=i.child).geom for i in all_ways]
                obj.geom = geos.MultiLineString(all_ways)
            else:
                obj = getattr(table_modules[osm_type], table_classes[osm_type]).objects.get(id=routeid)

            extent = obj.geom.extent

            showroute = obj.get_id()
        except:
            showroute = str(routeid)
    elif name is not None:
        try:
            obj = getattr(table_modules[osm_type], table_classes[osm_type]).objects.get(name__iexact=name)
            extent = obj.geom.extent
            showroute = obj.get_id()
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
