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

from collections import namedtuple
from django.utils.translation import ugettext as _
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render
from django.template.defaultfilters import slugify

import itertools
import django.contrib.gis.geos as geos
import urllib2
import json as jsonlib
from django.utils.importlib import import_module

table_modules = {}
table_classes = {}

# just to make sure we get translation strings
# XXX move that somewhere sensible
OSMTYPES = (
            # Translators: This means the OSM object type (http://wiki.osm.org/wiki/Way)
            _('way'),
            # Translators: This means the OSM object type (http://wiki.osm.org/wiki/Relation)
            _('relation'),
            _('joined way'))

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



def make_language_dict(request):
    """ Returns a hash with preferred languages and their weights.
        It takes into account the site language and the accept-language header.
    """

    # site language
    ret = { request.LANGUAGE_CODE : 2.0 }
    # aliases for site language
    if request.LANGUAGE_CODE in settings.LANGUAGE_ALIAS:
        for (l,w) in settings.LANGUAGE_ALIAS[request.LANGUAGE_CODE]:
            ret[l] = 1.0 + 0.5*w;

    if 'HTTP_ACCEPT_LANGUAGE' in request.META:
        for lang in request.META['HTTP_ACCEPT_LANGUAGE'].split(','):
            idx = lang.find(';')
            if idx < 0:
                w = 1.0
            else:
                try:
                    w = float(lang[idx+3:])
                except ValueError:
                    w = 0.0
                lang = lang[:idx]
            if w > 0.0 and (len(lang) == 2 or (len(lang) > 2 and lang[2] == '-')):
                lang = lang[:2]
                if lang not in ret or ret[lang] < w:
                    ret[lang] = w
                    if lang in settings.LANGUAGE_ALIAS:
                        for (l,wa) in settings.LANGUAGE_ALIAS[lang]:
                            if l not in ret:
                                ret[l] = w - 0.001*(2.0-wa)

    if 'en' not in ret:
       ret['en'] = 0.0

    return ret

def _make_display_length(length):
    if length < 1:
        return _("%s m") % int(round(length * 100) * 10)
    elif length < 10:
        return _("%s km") % ("%.1f" % length)
    else:
        return _("%s km") % int(round(length))

def info(request, route_id=None):
    langdict = make_language_dict(request)
    langlist = sorted(langdict, key=langdict.get)
    langlist.reverse()
    if route_id[0] == 'w':
        osm_type = 'way'
    elif route_id[0] == 'v':
        osm_type = 'joined_way'
    else:
        osm_type = 'relation'
    route_id = route_id[1:]

    qs = getattr(table_modules[osm_type], table_classes[osm_type]).objects
    if osm_type == 'joined_way':
        qs = qs.filter(virtual_id=route_id).extra(
                select={'length' :
                         """SELECT sum(ST_length2d_spheroid(ST_Transform(w.geom,4326),
                             'SPHEROID["WGS 84",6378137,298.257223563,
                             AUTHORITY["EPSG","7030"]]')/1000) FROM slopeways w, joined_slopeways j
                             WHERE j.virtual_id = joined_slopeways.virtual_id and j.child = w.id"""})
        print qs.query
    else:
        qs = qs.filter(id=route_id).extra(
                select={'length' :
                         """ST_length2d_spheroid(ST_Transform(geom,4326),
                             'SPHEROID["WGS 84",6378137,298.257223563,
                             AUTHORITY["EPSG","7030"]]')/1000"""})

    if len(qs) <= 0:
        return render(request, 'routes/info_error.html', {'id' : route_id})

    rel = qs[0]
    loctags = rel.tags().get_localized_tagstore(langdict)

    # Translators: The length of a route is presented with two values, this is the
    #              length that has been mapped so far and is actually visible on the map.
    infobox = [(_("Mapped length"), _make_display_length(rel.length))]
    dist = loctags.get_as_length(('distance', 'length'), unit='km')
    if dist:
        # Translators: The length of a route is presented with two values, this is the
        #              length given in the information about the route.
        #              More information about specifying route length in OSM here:
        #              http://wiki.openstreetmap.org/wiki/Key:distance
        infobox.append((_("Official length"), _make_display_length(dist)))
    if 'operator' in loctags:
        # Translators: This is someone responsible for maintaining the route. Normally
        #              an organisation. Read more: http://wiki.openstreetmap.org/wiki/Key:operator
        infobox.append((_("Operator"), loctags['operator']))
    rel.localize_name(langlist)

    if osm_type == 'joined_way':
        rel.str_id = 'v' + str(rel.virtual_id)
        rel.id = rel.virtual_id
    else:
        rel.str_id = osm_type[0] + str(rel.id)

    return render(request, 'routes/info.html',
            {'osm_type': osm_type,
             'route': rel,
             'infobox' : infobox,
             'loctags' : loctags,
             'show_elevation_profile' : settings.SHOW_ELEV_PROFILE,
             'superroutes' : rel.superroutes(langlist),
             'subroutes' : rel.subroutes(langlist),
             'symbolpath' : settings.ROUTEMAP_COMPILED_SYMBOL_PATH})

def wikilink(request, route_id=None):
    """ Return a redirect page to the Wikipedia page using the
        language preferences of the user.
    """
    langdict = make_language_dict(request)
    langlist = sorted(langdict, key=langdict.get)
    langlist.reverse()
    if route_id[0] == 'w':
        osm_type='way'
    else:
        osm_type='relation'
    route_id = route_id[1:]

    try:
        rel = getattr(table_modules[osm_type], table_classes[osm_type]).objects.get(id=route_id)
    except:
        raise Http404

    wikientries = rel.tags().get_wikipedia_tags()

    if len(wikientries) == 0:
        raise Http404

    link = None
    outlang = None
    for lang in langlist:
        if lang in wikientries:
            outlang = lang
            link = wikientries[lang]
            break

        for k,v in wikientries.iteritems():
            if not v.startswith('http'):
                try:
                    url = "http://%s.wikipedia.org/w/api.php?action=query&prop=langlinks&titles=%s&llurl=true&&lllang=%s&format=json" % (k,urllib2.quote(v.encode('utf8')),lang)
                    req = urllib2.Request(url, headers={
                        'User-Agent' : 'Python-urllib/2.7 Routemaps (report problems to %s)' % settings.ADMINS[0][1]
                        })
                    data = urllib2.urlopen(req).read()
                    data = jsonlib.loads(data)
                    (pgid, data) = data["query"]["pages"].popitem()
                    if 'langlinks' in data:
                        link = data['langlinks'][0]['url']
                        break
                except:
                    break # oh well, we tried
        if link is not None:
            break


    # given up to find a requested language
    if link is None:
        outlang, link = wikientries.popitem()

    # paranoia, avoid HTML injection
    link.replace('"', '%22')
    link.replace("'", '%27')
    if not link.startswith('http:'):
        link = 'http://%s.wikipedia.org/wiki/%s' % (outlang, link)

    return HttpResponseRedirect(link)


def gpx(request, route_id=None):
    if route_id[0] == 'w':
        osm_type='way'
    elif route_id[0] == 'v':
        osm_type = 'joined_way'
    else:
        osm_type='relation'
    route_id = route_id[1:]
    if osm_type == 'joined_way':
        all_ways = getattr(table_modules['joined_way'], table_classes['joined_way']).objects.filter(virtual_id=route_id)
        route = getattr(table_modules['way'], table_classes['way']).objects.filter(id=all_ways[0].child).transform(srid=4326)[0]
        all_ways = [getattr(table_modules['way'], table_classes['way']).objects.filter(id=i.child).transform(srid=4326)[0].geom for i in all_ways]
        outgeom = geos.MultiLineString(all_ways)
        prefix = 'v'
    else:
        route = getattr(table_modules[osm_type], table_classes[osm_type]).objects.filter(id=route_id).transform(srid=4326)[0]
        outgeom = route.geom
        prefix = osm_type[0]
    try:
        pass
    except:
        return render(request, 'routes/info_error.html', {'id' : route_id})
    if isinstance(outgeom, geos.LineString):
        outgeom = (outgeom, )

    route.str_id = prefix + str(route.id)
    resp = render(request, 'routes/gpx.xml', {'route' : route, 'geom' : outgeom, 'osm_type' : osm_type}, content_type='application/gpx+xml')
    resp['Content-Disposition'] = 'attachment; filename=%s.gpx' % slugify(route.name)
    return resp

def json(request, route_id=None):
    if route_id[0] == 'w':
        osm_type = 'way'
    elif route_id[0] == 'v':
        osm_type = 'joined_way'
    else:
        osm_type = 'relation'
    route_id = route_id[1:]
    try:
        if osm_type == 'joined_way':
            route = getattr(table_modules[osm_type], table_classes[osm_type]).objects.filter(virtual_id=route_id)[0]
        else:
            route = getattr(table_modules[osm_type], table_classes[osm_type]).objects.get(id=route_id)
    except:
        return render(request, 'routes/info_error.html', {'id' : osm_type + ' ' + route_id})

    if osm_type == 'joined_way':
        all_ways = getattr(table_modules['joined_way'], table_classes['joined_way']).objects.filter(virtual_id=route_id)
        all_ways = [getattr(table_modules['way'], table_classes['way']).objects.get(id=i.child).geom for i in all_ways]
        route.geom = geos.MultiLineString(all_ways)

    nrpoints = route.geom.num_coords
    #print nrpoints
    if nrpoints > 50000:
        route.geom = route.geom.simplify(100.0)
    if nrpoints > 10000:
        route.geom = route.geom.simplify(20.0)
    elif nrpoints > 1000:
        route.geom = route.geom.simplify(10.0)
    elif nrpoints > 300:
        route.geom = route.geom.simplify(5.0)
    #print route.geom.num_coords
    return HttpResponse(route.geom.json, content_type="text/json")

def json_box(request):
    try:
        coords = get_coordinates(request.GET.get('bbox', ''))
    except CoordinateError as e:
        return render(request, 'routes/error.html',
                {'msg' : e.value})

    rels = []
    ways = []
    joined_ways = []
    for s in request.GET.get('ids', '').split(','):
        try:
            if (len(s) > 0 and s[0] == 'w'):
                ways.append(int(s[1:]))
            elif (len(s) > 0 and s[0] == 'v'):
                joined_ways.append(int(s[1:]))
            else:
                rels.append(int(s[1:]))
        except ValueError:
            pass # ignore

    if not rels and not ways and not joined_ways:
        return HttpResponse('[]', content_type="text/json")

    rels = rels[:settings.ROUTEMAP_MAX_ROUTES_IN_LIST]
    ways = ways[:settings.ROUTEMAP_MAX_ROUTES_IN_LIST]
    joined_ways = joined_ways[:settings.ROUTEMAP_MAX_ROUTES_IN_LIST]

    selquery = ("""ST_Intersection(st_transform(ST_SetSRID(
                     'BOX3D(%f %f, %f %f)'::Box3d,4326),%%s) , geom)
               """ % coords) % settings.DATABASES['default']['SRID']
    ydiff = 10*(coords[3]-coords[1])

    if ydiff > 1:
        selquery = "ST_Simplify(%s, %f)"% (selquery, ydiff*ydiff*ydiff/2)
    selquery = "ST_AsGeoJSON(%s)" % selquery

    ways = getattr(table_modules['way'], table_classes['way']).objects.filter(id__in=ways).extra(
            select={'way' : selquery, 'id' : "'w' || id"}).only('downhill')

    rels = getattr(table_modules['relation'], table_classes['relation']).objects.filter(id__in=rels).extra(
            select={'way' : selquery, 'id' : "'r' || id"}).only('downhill')

    class joined_result:
        way = None
        id = None

    joined_ways_res = []
    for j in joined_ways:
        all_ways = getattr(table_modules['joined_way'], table_classes['joined_way']).objects.filter(virtual_id=j)
        #joined_ways_res += getattr(table_modules['way'], table_classes['way']).objects.filter(
        #id__in=[i.child for i in all_ways]).extra(select={'way' : "ST_UNION(" + selquery + ")",  'id' : "'v" + str(j) + "'"}).aggregate(Max('id'))

        all_ways = [getattr(table_modules['way'], table_classes['way']).objects.filter(id=i.child)
        #.extra(select={'way' : selquery})[0].way for i in all_ways]
        [0].geom for i in all_ways]
        res = joined_result()
        res.id = 'v' + str(j)
        res.way = geos.MultiLineString(all_ways).json
        joined_ways_res += [res]


    return render(request, 'routes/route_box.json',
                              { 'rels' : itertools.chain(rels, itertools.chain(ways, joined_ways_res)) },
                              content_type="text/html")



RouteList = namedtuple('RouteList', 'title shorttitle routes')

def list(request):
    try:
        coords = get_coordinates(request.GET.get('bbox', ''))
    except CoordinateError as e:
        return render(request, 'routes/error.html',
                {'msg' : e.value})


    qs1 = getattr(table_modules['way'], table_classes['way']).objects.extra(where=(("""
             geom && st_transform(ST_SetSRID(
                             'BOX3D(%f %f, %f %f)'::Box3d,4326),%%s)"""
                             % coords) % settings.DATABASES['default']['SRID'],)
                             )[:settings.ROUTEMAP_MAX_ROUTES_IN_LIST]

    qs2 = getattr(table_modules['relation'], table_classes['relation']).objects.extra(where=(("""
             geom && st_transform(ST_SetSRID(
                             'BOX3D(%f %f, %f %f)'::Box3d,4326),%%s)"""
                             % coords) % settings.DATABASES['default']['SRID'],)
                             )[:settings.ROUTEMAP_MAX_ROUTES_IN_LIST]

    objs = (RouteList(_('unknown'), 'unknown', []),
            RouteList(_('skiing'), 'ski', []),
            RouteList(_('nordic'), 'nordic', []),
            RouteList(_('sledding'), 'sled', []),
            RouteList(_('snowshoeing'), 'hike', []),
            RouteList(_('track for self-propelled sleighs'), 'sleigh', []),
           )
    osmids = []
    langdict = make_language_dict(request)
    langlist = sorted(langdict, key=langdict.get)
    langlist.reverse()

    # replace ways with joined ways
    joined_ways = set()
    to_delete = []
    for l in range(len(qs1)):
        parent_rel = getattr(table_modules['joined_way'], table_classes['joined_way']).objects.filter(child=qs1[l].id)
        if parent_rel.count() > 0:
            vid = parent_rel[0].virtual_id
            if vid in joined_ways:
                to_delete += [l]
            else:
                joined_ways.update([vid])
                qs1[l].id = vid
                qs1[l].osm_type = 'v'

    qs1 = [i for i in qs1]
    for l in reversed(to_delete):
        del qs1[l]

    length = len(qs1) + len(qs2)
    if (length > settings.ROUTEMAP_MAX_ROUTES_IN_LIST):
        limit1 = len(qs1) - (length - settings.ROUTEMAP_MAX_ROUTES_IN_LIST) / 2
        limit2 = len(qs2) - (length - settings.ROUTEMAP_MAX_ROUTES_IN_LIST) / 2
        hasmore = True
    else:
        limit1 = settings.ROUTEMAP_MAX_ROUTES_IN_LIST
        limit2 = settings.ROUTEMAP_MAX_ROUTES_IN_LIST
        hasmore = False

    for rel in itertools.chain(qs1[:limit1], qs2[:limit2]):
        rel.localize_name(langlist)
        rel.id = rel.osm_type + str(rel.id)
        if rel.downhill:
            objs[1].routes.append(rel)
        elif rel.nordic:
            objs[2].routes.append(rel)
        elif rel.sled:
            objs[3].routes.append(rel)
        elif rel.hike:
            objs[4].routes.append(rel)
        elif rel.sleigh:
            objs[5].routes.append(rel)
        else:
            objs[0].routes.append(rel)
        osmids.append(rel.id)

    return render(request,
            'routes/list.html',
             {'objs' : objs,
              'osmids' : ','.join(osmids),
              'hasmore' : hasmore,
              'symbolpath' : settings.ROUTEMAP_COMPILED_SYMBOL_PATH,
              'bbox' : request.GET.get('bbox', '')})

