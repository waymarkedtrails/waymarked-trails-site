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

from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from django.contrib.gis.geos import Polygon
from django.conf import settings
from django.http import HttpResponse

import json as jsonlib
from django.utils.importlib import import_module

table_module, table_class = settings.ROUTEMAP_SEGMENT_TABLE.rsplit('.',1)
table_module = import_module(table_module)

class CoordinateError(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

def get_coordinates(arg):
    coords = arg.split(',')
    if len(coords) != 4:
        # Translators: This message will very rarely be shown, and likely only to people who have manipulated the URL. For more info about bbox: http://wiki.openstreetmap.org/wiki/Bounding_Box
        raise CoordinateError(_("No valid map area specified. Check the bbox parameter in the URL."))

    try:
        coords = tuple([float(x) for x in coords])
    except ValueError:
        # Translators: This message will very rarely be shown, and likely only to people who have manipulated the URL. For more info about bbox: http://wiki.openstreetmap.org/wiki/Bounding_Box
        raise CoordinateError(_("Invalid coordinates given for the map area. Check the bbox parameter in the URL."))

    # restirct coordinates
    # It may actually happen that out-of-bounds coordinates
    # are delivered. Try browsing in New Zealand.
    coords = (max(min(180, coords[0]), -180),
              max(min(90, coords[1]), -90),
              max(min(180, coords[2]), -180),
              max(min(90, coords[3]), -90))

    if (coords[0] >= coords[2]) or (coords[1] >= coords[3]):
        raise CoordinateError(_("Invalid coordinates given for the map area. Check the bbox parameter in the URL."))

    return coords


def jsonbox(request):
    try:
        coords = get_coordinates(request.GET.get('bbox', ''))
    except CoordinateError as e:
        return direct_to_template(request, 'routes/error.html', 
                {'msg' : e.value})

    
    geoquery = ("""ST_Transform(ST_SetSRID('BOX3D(%f %f, %f %f)'::Box3d,4326),%%s) && geom
               """ % coords) % settings.DATABASES['default']['SRID']

    bbox = Polygon.from_bbox(coords)

    print bbox

    qs = getattr(table_module, table_class).objects.extra(
            select={'way' : 'ST_AsGeoJSON(ST_Transform(geom,4326))'},
            where=[geoquery])
    # print qs.query

    data = []
    for obj in qs[:500]:
        data.append({
              "type" : "Feature",
              "geometry" : jsonlib.loads(obj.way),
              "properties" : { "id" : obj.id,
                               "rels" : obj.rels }
                })
    data = { "type" : "FeatureCollection",
             "features" : data }

    resp = HttpResponse(jsonlib.dumps(data), mimetype='application/json')
    resp['Access-Control-Allow-Origin'] = "*"

    return resp
