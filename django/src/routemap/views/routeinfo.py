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
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.template.defaultfilters import slugify

import django.contrib.gis.geos as geos


def info(request, route_id=None, manager=None):
    qs = manager.extra(
                select={'length' : 
                         """ST_length_spheroid(ST_Transform(geom,4326),
                             'SPHEROID["WGS 84",6378137,298.257223563,
                             AUTHORITY["EPSG","7030"]]')/1000"""})
    try:
        rel = qs.get(id=route_id)
        rel.localize_name(request.LANGUAGE_CODE)
    except:
        return direct_to_template(request, 'routes/info_error.html', {'id' : route_id})

    return direct_to_template(request, 'routes/info.html', 
            {'route': rel, 
             'loctags' : rel.get_local_tags(request.LANGUAGE_CODE),
             'superroutes' : rel.superroutes(request.LANGUAGE_CODE),
             'subroutes' : rel.subroutes(request.LANGUAGE_CODE),
             'symbolpath' : settings.ROUTEMAP_COMPILED_SYMBOL_PATH})

def gpx(request, route_id=None, manager=None):
    try:
        rel = manager.filter(id=route_id).transform(srid=4326)[0]
    except:
        return direct_to_template(request, 'routes/info_error.html', {'id' : route_id})
    if isinstance(rel.geom, geos.LineString):
        rel.geom = geos.MultiLineString(rel.geom)
    resp = direct_to_template(request, 'routes/gpx.xml', {'route' : rel, 'geom' : rel.geom,
            'maptopic' : settings.ROUTEMAP_PAGEINFO['maptopic']}, mimetype='application/gpx+xml')
    resp['Content-Disposition'] = 'attachment; filename=%s.gpx' % slugify(rel.name)
    return resp

def json(request, route_id=None, manager=None):
    try:
        rel = manager.get(id=route_id)
    except:
        return direct_to_template(request, 'routes/info_error.html', {'id' : route_id})
    nrpoints = rel.geom.num_coords
    #print nrpoints
    if nrpoints > 50000:
        rel.geom = rel.geom.simplify(100.0)
    if nrpoints > 10000:
        rel.geom = rel.geom.simplify(20.0)
    elif nrpoints > 1000:
        rel.geom = rel.geom.simplify(10.0)
    elif nrpoints > 300:
        rel.geom = rel.geom.simplify(5.0)
    #print rel.geom.num_coords
    return HttpResponse(rel.geom.json, content_type="text/json")

def list(request, manager=None, hierarchytab=None, segmenttab=None):
    errormsg = _("No valid bounding box specified.")

    coords = request.GET.get('bbox', '').split(',')
    if len(coords) == 4:
        try:
            coords = tuple([float(x) for x in coords])
        except ValueError:
            return direct_to_template(request, 'routes/error.html', 
                {'msg' : _("Invalid coordinates in bounding box.")})

        # restirct coordinates
        # It may actually happen that out-of-bounds coordinates
        # are delivered. Try browsing in New Zealand.
        coords = (max(min(180, coords[0]), -180),
                  max(min(90, coords[1]), -90),
                  max(min(180, coords[2]), -180),
                  max(min(90, coords[3]), -90))

        if (coords[0] >= coords[2]) or (coords[1] >= coords[3]):
            return direct_to_template(request, 'routes/error.html', 
                {'msg' : _("Invalid coordinates in bounding box.")})

        bbox=geos.GEOSGeometry('SRID=4326;MULTIPOINT(%f %f, %f %f)' % coords)

        qs = manager.filter(top=True).extra(where=(("""
                id = ANY(SELECT DISTINCT h.parent
                         FROM %%s h,
                              (SELECT DISTINCT unnest(rels) as rel
                               FROM %%s
                               WHERE geom && st_transform(SetSRID(
                                 'BOX3D(%f %f, %f %f)'::Box3d,4326),900913)) as r
                         WHERE h.child = r.rel)"""
                % coords) % (hierarchytab, segmenttab),)).order_by('level')
        #print qs.query
        
        objs = ([],[],[],[])
        numobj = 0

        for rel in qs[:settings.ROUTEMAP_MAX_ROUTES_IN_LIST]:
            listnr = min(3, rel.level / 10)
            rel.localize_name(request.LANGUAGE_CODE)
            objs[listnr].append(rel)
            numobj += 1

        return direct_to_template(request,
                'routes/list.html', 
                 {'objs' : objs,
                  'hasmore' : numobj == settings.ROUTEMAP_MAX_ROUTES_IN_LIST,
                  'symbolpath' : settings.ROUTEMAP_COMPILED_SYMBOL_PATH})

    return direct_to_template(request, 'routes/error.html', 
                {'msg' : errormsg})

