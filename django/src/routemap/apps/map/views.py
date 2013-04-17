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
from django.views.generic.simple import direct_to_template

from django.conf import settings

from django.utils.importlib import import_module

table_module, table_class = settings.ROUTEMAP_ROUTE_TABLE.rsplit('.',1)
table_module = import_module(table_module)

def route_map_view(request, relid=None, name=None, template='basemap.html'):
    if request.COOKIES.has_key('_routemap_location'):
        cookie = request.COOKIES['_routemap_location'].split('|')
    else:
        cookie = None

    extent = (693000, 5764000, 1150000, 6062100) 
    firstVisit = 1
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

    if showroute == -1:
        # check for a cookie
        if cookie is not None:
            if len(cookie) >= 4:
                # XXX make sure the cookie is correct
                extent = cookie[:4]
                firstVisit = 0

    context = {'minlat' : str(extent[1]), 'maxlat' : str(extent[3]),
               'minlon' : str(extent[0]), 'maxlon' : str(extent[2]),
               'showroute' : showroute, 'baseopacity' : '1.0',
               'routeopacity' : '0.8', 'hillopacity' : '0.0',
               'tileurl' : settings.ROUTEMAP_TILE_URL,
               'firstVisit' : firstVisit
    }


    try:
        uf = open(settings.ROUTEMAP_UPDATE_TIMESTAMP)
        context['updatetime'] = datetime.strptime(uf.readline().strip(),
                                 '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=utc)
        uf.close()
    except:
        pass

    if cookie is not None:
        if len(cookie) >= 7:
            context['baseopacity'] = cookie[4]
            context['routeopacity'] = cookie[5]
            context['hillopacity'] = cookie[6]    
            
    context['show_elevation_profile'] = settings.SHOW_ELEV_PROFILE

    context['ismobile'] = request.flavour == 'mobile'
    return direct_to_template(request,
                              template=template, 
                              extra_context=context
                              )
