# This file is part of waymarkedtrails.org
# Copyright (C) 2017 Sarah Hoffmann
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

from collections import OrderedDict
from datetime import datetime
from array import array
import urllib.parse
import urllib.request
import json as jsonlib
import unicodedata
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from slugify import slugify
import cherrypy
import sqlalchemy as sa
from geoalchemy2.shape import to_shape
from geoalchemy2.types import Geometry
from osgende.common.tags import TagStore

from shapely.ops import linemerge
from shapely.geometry import Point, LineString

import config.defaults
import api.common
from api.elevation import compute_elevation

class ST_LineInterpolatePoint(sa.sql.functions.GenericFunction):
    type = Geometry

class ST_Collect(sa.sql.functions.GenericFunction):
    type = Geometry

class ST_LineMerge(sa.sql.functions.GenericFunction):
    type = Geometry

class GenericDetails(object):

    def make_filename(self, suffix, name, oid):
        if name:
            return slugify(name) + suffix

        return str(oid) + suffix

    def create_details_response(self, res):
        if res is None:
            raise cherrypy.NotFound()

        loctags = TagStore.make_localized(res['tags'], cherrypy.request.locales)
        cfg = cherrypy.request.app.config

        ret = api.common.RouteDict(res)
        ret['type'] = res['type'] if res.has_key('type') else 'relation'
        ret['symbol_url'] = '%s/symbols/%s/%s.svg' % (cfg['Global']['MEDIA_URL'],
                                                      cfg['Global']['BASENAME'],
                                                      str(res['symbol']))
        ret['mapped_length'] = int(res['length'])
        ret.add_if('official_length',
                   loctags.get_length('distance', 'length', unit='m'))
        for tag in ('operator', 'note', 'description'):
            ret.add_if(tag, loctags.get(tag))
        ret.add_if('url', loctags.get_url())
        ret.add_if('wikipedia', loctags.get_wikipedia_tags())
        ret['bbox'] = to_shape(res['bbox']).bounds

        if hasattr(self, '_hierarchy_list'):
            for name, val in (('subroutes', True), ('superroutes', False)):
                ret.add_if(name, self._hierarchy_list(ret['id'], val))

        ret['tags'] = res['tags']

        return ret

    def create_wikilink_response(self, res):
        if res is None:
            raise cherrpy.NotFound()

        wikientries = TagStore(res['tags']).get_wikipedia_tags()

        if not wikientries:
            raise cherrypy.NotFound()

        wikilink = 'https://%s.wikipedia.org/wiki/%s'
        for lang in cherrypy.request.locales:
            if lang in wikientries:
                title = urllib.parse.quote(wikientries[lang].replace(' ', '_'))
                raise cherrypy.HTTPRedirect(wikilink % (lang, title))

            for k,v in wikientries.items():
                url = "https://%s.wikipedia.org/w/api.php?action=query&prop=langlinks&titles=%s&llprop=url&&lllang=%s&format=json" % (k,urllib.parse.quote(v.encode('utf8')),lang)
                try:
                    req = urllib.request.Request(url, headers={
                        'User-Agent' : 'Python-urllib/2.7 Routemaps'
                        })
                    data = urllib.request.urlopen(req).read().decode('utf-8')
                    data = jsonlib.loads(data)
                except:
                    continue # oh well, we tried
                (pgid, data) = data["query"]["pages"].popitem()
                if 'langlinks' in data:
                    raise cherrypy.HTTPRedirect(data['langlinks'][0]['url'])
        else:
            # given up to find a requested language
            k, v = wikientries.popitem()
            raise cherrypy.HTTPRedirect(wikilink % (k, urllib.parse.quote(v.replace(' ', '_'))))


    def create_gpx_response(self, oid, res):
        if res is None:
            raise cherrypy.NotFound()

        for l in cherrypy.request.locales:
            if l in res['intnames']:
                name = res['intnames'][l]
                break
        else:
            name = res['name'] if res['name'] is not None else res['ref']

        root = ET.Element('gpx',
                          { 'xmlns' : "http://www.topografix.com/GPX/1/1",
                            'creator' : "waymarkedtrails.org",
                            'version' : "1.1",
                            'xmlns:xsi' : "http://www.w3.org/2001/XMLSchema-instance",
                            'xsi:schemaLocation' :  "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"
                           })
        # metadata
        meta = ET.SubElement(root, 'metadata')
        ET.SubElement(meta, 'name').text = name

        copy = ET.SubElement(meta, 'copyright', author='OpenStreetMap and Contributors')
        ET.SubElement(copy, 'license').text = 'http://www.openstreetmap.org/copyright'

        wenv = cherrypy.request.wsgi_environ
        link = ET.SubElement(meta, 'link',
                             href="%s://%s%s/#route?id=%s" % (
                                     wenv["wsgi.url_scheme"], wenv["HTTP_HOST"],
                                     config.defaults.BASE_URL, oid))
        ET.SubElement(link, 'text').text = 'Waymarked Trails'

        ET.SubElement(meta, 'time').text = datetime.utcnow().isoformat()

        # and the geometry
        trk = ET.SubElement(root, 'trk')
        geom = to_shape(res['geom'])

        if geom.geom_type == 'LineString':
            geom = (geom,)

        for line in geom:
            seg = ET.SubElement(trk, 'trkseg')
            for pt in line.coords:
                ET.SubElement(seg, 'trkpt',
                              lat="%.7f" % pt[1],
                              lon="%.7f" % pt[0])

        cherrypy.response.headers['Content-Type'] = 'application/gpx+xml'
        cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=' + self.make_filename('.gpx', name, oid)

        return '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n\n'.encode('utf-8') \
                 + ET.tostring(root, encoding="UTF-8")

    
    def create_kml_response(self, oid, res):
        if res is None:
            raise cherrypy.NotFound()

        for l in cherrypy.request.locales:
            if l in res['intnames']:
                name = res['intnames'][l]
                break
        else:
            name = res['name']

        root = ET.Element('kml',
                          { 'xmlns' : "http://www.opengis.net/kml/2.2",
                            'creator' : "waymarkedtrails.org",
                            'version' : "1.1",
                            'xmlns:atom' : "http://www.w3.org/2005/Atom"
                           })
        # metadata
        doc = ET.SubElement(root, 'Document')
        ET.SubElement(doc, 'name').text = name
        ET.SubElement(doc, 'atom:author').text = 'waymarkedtrails.org; OpenStreetMap and Contributors http://www.openstreetmap.org/copyright'
        ET.SubElement(doc, 'atom:link', {
            'href' : config.defaults.BASE_URL + '/#route?id=' + oid
        })
        mark = ET.SubElement(doc, 'Placemark')
        ET.SubElement(mark, 'name').text = name

        # and the geometry
        multi = ET.SubElement(mark, 'MultiGeometry')

        geom = to_shape(res['geom'])

        if geom.geom_type == 'LineString':
            geom = (geom,)

        for line in geom:
            linestring = ET.SubElement(multi, 'LineString')
            coords = ""
            for pt in line.coords:
                coords += "%.7f,%.7f\n" % (pt[0], pt[1]) 
            ET.SubElement(linestring, 'coordinates').text = coords

        cherrypy.response.headers['Content-Type'] = 'application/vnd.google-earth.kml+xml'
        cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=' + self.make_filename('.kml', name, oid)

        return '<?xml version="1.0" encoding="UTF-8" ?>\n\n'.encode('utf-8') \
                 + ET.tostring(root, encoding="UTF-8")


    def create_geometry_response(self, res):
        if res is None:
            raise cherrypy.NotFound()

        cherrypy.response.headers['Content-Type'] = 'text/json'
        fulljson = """
         { "type": "FeatureCollection",
           "crs": { "type": "name",
                    "properties": { "name": "EPSG:3857"}
                  },
           "features": [{ "type": "Feature", "geometry" : %s }]
         }""" % res[0]

        return fulljson.encode('utf-8')


@cherrypy.popargs('oid')
class RelationInfo(GenericDetails):

    def __init__(self, level_column):
        self.level_column = level_column

    def _hierarchy_list(self, rid, subs):
        mapdb = cherrypy.request.app.config['DB']['map']
        r = mapdb.tables.routes.data
        h = mapdb.tables.hierarchy.data

        if subs:
            w = sa.select([h.c.child], distinct=True).where(h.c.parent == rid).where(h.c.depth == 2)
        else:
            w = sa.select([h.c.parent], distinct=True).where(h.c.child == rid).where(h.c.depth == 2)

        sections = sa.select([r.c.id, r.c.name, r.c.intnames, r.c.ref, r.c.itinary,
                              r.c[self.level_column].label('level')])\
                   .where(r.c.id != rid).where(r.c.id.in_(w))

        return [api.common.RouteDict(x)
                 for x in cherrypy.request.db.execute(sections)]


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip(mime_types=['application/json'])
    def index(self, oid, **params):
        cfg = cherrypy.request.app.config
        mapdb = cfg['DB']['map']
        r = mapdb.tables.routes.data
        o = mapdb.osmdata.relation.data
        sel = sa.select([r.c.id, r.c.name, r.c.intnames, r.c.symbol, r.c.ref,
                         r.c[self.level_column].label('level'), r.c.itinary,
                         o.c.tags,
                         sa.func.ST_Length2dSpheroid(sa.func.ST_Transform(r.c.geom,4326),
                             'SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]]').label("length"),
                         r.c.geom.ST_Envelope().label('bbox')])

        res = cherrypy.request.db.execute(sel.where(r.c.id==oid)
                                             .where(o.c.id==oid)).first()

        return self.create_details_response(res)

    @cherrypy.expose
    def wikilink(self, oid, **params):
        r = cherrypy.request.app.config['DB']['map'].osmdata.relation.data
        res = cherrypy.request.db.execute(sa.select([r.c.tags]).where(r.c.id==oid)).first()
        return self.create_wikilink_response(res)


    def export(self, oid):
        r = cherrypy.request.app.config['DB']['map'].tables.routes.data
        sel = sa.select([r.c.name, r.c.intnames, r.c.ref, r.c.id,
                         r.c.geom.ST_Transform(4326).label('geom')])
        return cherrypy.request.db.execute(sel.where(r.c.id==oid)).first()

    @cherrypy.expose
    @cherrypy.tools.gzip(mime_types=['application/gpx+xml'])
    def gpx(self, oid, **params):
        return self.create_gpx_response(oid, self.export(oid))

    @cherrypy.expose
    @cherrypy.tools.gzip(mime_types=['application/vnd.google-earth.kml+xml'])
    def kml(self, oid, **params):
        return self.create_kml_response(oid, self.export(oid))


    @cherrypy.expose
    @cherrypy.tools.gzip(mime_types=['text/json'])
    def geometry(self, oid, factor=None, **params):
        r = cherrypy.request.app.config['DB']['map'].tables.routes.data
        if factor is None:
            field = r.c.geom
        else:
            field = r.c.geom.ST_Simplify(r.c.geom.ST_NPoints()/int(factor))
        field = field.ST_AsGeoJSON()
        res = cherrypy.request.db.execute(sa.select([field]).where(r.c.id==oid)).first()

        return self.create_geometry_response(res)


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip(mime_types=['application/json'])
    def elevation(self, oid, segments=None, **params):
        if segments is not None and segments.isdigit():
            segments = int(segments)
            if segments > 500 or segments <= 0:
                segments = 500
        else:
            segments = 100

        ret = OrderedDict()
        ret['id'] = oid

        r = cherrypy.request.app.config['DB']['map'].tables.routes.data
        gen = sa.select([sa.func.generate_series(0, segments).label('i')]).alias()
        field = sa.func.ST_LineInterpolatePoint(r.c.geom, gen.c.i/float(segments))
        field = sa.func.ST_Collect(field)

        sel = sa.select([field]).where(r.c.id == oid)\
                .where(r.c.geom.ST_GeometryType() == 'ST_LineString')

        res = cherrypy.request.db.execute(sel).first()

        if res is not None and res[0] is not None:
            geom = to_shape(res[0])
            xcoord, ycoord = zip(*((p.x, p.y) for p in geom))
            geomlen = LineString(geom).length
            pos = [geomlen*i/float(segments) for i in range(segments)]
            compute_elevation(((xcoord, ycoord, pos), ), geom.bounds, ret)
            return ret

        # special treatment for multilinestrings
        sel = sa.select([r.c.geom,
                         sa.literal_column("""ST_Length2dSpheroid(ST_MakeLine(ARRAY[ST_Points(ST_Transform(geom,4326))]),
                             'SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY["EPSG",\"7030\"]]')"""),
                         r.c.geom.ST_NPoints()])\
                .where(r.c.id == oid)

        res = cherrypy.request.db.execute(sel).first()

        if res is not None and res[0] is not None:
            geom = to_shape(res[0])

            if res[2] > 10000:
                geom = geom.simplify(res[2]/500, preserve_topology=False)
            elif res[2] > 4000:
                geom = geom.simplify(res[2]/1000, preserve_topology=False)

            segments = []

            for seg in geom:
                p = seg.coords[0]
                xcoords = array('d', [p[0]])
                ycoords = array('d', [p[1]])
                pos = array('d')
                if segments:
                    prev = segments[-1]
                    pos.append(prev[2][-1] + \
                            Point(prev[0][-1], prev[1][-1]).distance(Point(*p)))
                else:
                    pos.append(0.0)
                for p in seg.coords[1:]:
                    pos.append(pos[-1] + Point(xcoords[-1], ycoords[-1]).distance(Point(*p)))
                    xcoords.append(p[0])
                    ycoords.append(p[1])

                segments.append((xcoords, ycoords, pos))

            compute_elevation(segments, geom.bounds, ret)

            ret['length'] = float(res[1])
            return ret

        raise cherrypy.NotFound()


@cherrypy.popargs('oid')
class WayInfo(GenericDetails):

    def __init__(self, level_column):
        self.level_column = level_column

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip(mime_types=['application/json'])
    def index(self, oid, **params):
        cfg = cherrypy.request.app.config
        mapdb = cfg['DB']['map']
        w = mapdb.tables.ways.data
        o = mapdb.osmdata.way.data
        sel = sa.select([sa.literal('way').label('type'),
                         w.c.id, w.c.name, w.c.intnames, w.c.symbol,
                         w.c[self.level_column].label('level'),
                         o.c.tags,
                         sa.func.ST_Length2dSpheroid(sa.func.ST_Transform(w.c.geom,4326),
                             'SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]]').label("length"),
                         w.c.geom.ST_Envelope().label('bbox')])

        res = cherrypy.request.db.execute(sel.where(w.c.id==oid)
                                             .where(o.c.id==oid)).first()

        return self.create_details_response(res)

    @cherrypy.expose
    def wikilink(self, oid, **params):
        w = cherrypy.request.app.config['DB']['map'].osmdata.way.data
        res = cherrypy.request.db.execute(sa.select([w.c.tags]).where(w.c.id==oid)).first()
        return self.create_wikilink_response(res)


    def export(self, oid):
        w = cherrypy.request.app.config['DB']['map'].tables.ways.data
        sel = sa.select([w.c.name, w.c.intnames,
                         w.c.geom.ST_Transform(4326).label('geom')])
        return cherrypy.request.db.execute(sel.where(w.c.id==oid)).first()

    @cherrypy.expose
    @cherrypy.tools.gzip(mime_types=['application/gpx+xml'])
    def gpx(self, oid, **params):
        return self.create_gpx_response(oid, self.export(oid))

    @cherrypy.expose
    @cherrypy.tools.gzip(mime_types=['application/vnd.google-earth.kml+xml'])
    def kml(self, oid, **params):
        return self.create_kml_response(oid, self.export(oid))


    @cherrypy.expose
    @cherrypy.tools.gzip(mime_types=['text/json'])
    def geometry(self, oid, factor=None, **params):
        w = cherrypy.request.app.config['DB']['map'].tables.ways.data
        if factor is None:
            field = w.c.geom
        else:
            field = w.c.geom.ST_Simplify(w.c.geom.ST_NPoints()/int(factor))
        field = field.ST_AsGeoJSON()
        res = cherrypy.request.db.execute(sa.select([field]).where(w.c.id==oid)).first()

        return self.create_geometry_response(res)


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip(mime_types=['application/json'])
    def elevation(self, oid, segments=None, **params):
        if segments is not None and segments.isdigit():
            segments = int(segments)
            if segments > 500 or segments <= 0:
                segments = 500
        else:
            segments = 100

        w = cherrypy.request.app.config['DB']['map'].tables.ways.data
        gen = sa.select([sa.func.generate_series(0, segments).label('i')]).alias()
        field = sa.func.ST_LineInterpolatePoint(w.c.geom, gen.c.i/float(segments))
        field = sa.func.ST_Collect(field)

        sel = sa.select([field]).where(w.c.id == oid)
        res = cherrypy.request.db.execute(sel).first()

        if res is None or res[0] is None:
            raise cherrypy.NotFound()

        ret = OrderedDict()
        ret['id'] = oid
        geom = to_shape(res[0])
        xcoord, ycoord = zip(*((p.x, p.y) for p in geom))
        geomlen = LineString(geom).length
        pos = [geomlen*i/float(segments) for i in range(segments)]
        compute_elevation(((xcoord, ycoord, pos), ), geom.bounds, ret)

        return ret

@cherrypy.popargs('oid')
class WaySetInfo(GenericDetails):

    def __init__(self, level_column):
        self.level_column = level_column

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip(mime_types=['application/json'])
    def index(self, oid, **params):
        cfg = cherrypy.request.app.config
        mapdb = cfg['DB']['map']
        w = mapdb.tables.ways.data
        o = mapdb.osmdata.way.data
        sel = sa.select([sa.literal('wayset').label('type'),
                         w.c.id, w.c.name, w.c.intnames, w.c.symbol,
                         w.c[self.level_column].label('level'),
                         o.c.tags,
                         sa.func.ST_Length2dSpheroid(sa.func.ST_Transform(w.c.geom,4326),
                             'SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]]').label("length"),
                         w.c.geom.ST_Envelope().label('bbox')])

        res = cherrypy.request.db.execute(sel.where(w.c.id==oid)
                                             .where(o.c.id==oid)).first()

        return self.create_details_response(res)

    @cherrypy.expose
    def wikilink(self, oid, **params):
        w = cherrypy.request.app.config['DB']['map'].osmdata.way.data
        res = cherrypy.request.db.execute(sa.select([w.c.tags]).where(w.c.id==oid)).first()
        return self.create_wikilink_response(res)


    def export(self, oid):
        w = cherrypy.request.app.config['DB']['map'].tables.ways.data
        ws = cherrypy.request.app.config['DB']['map'].tables.joined_ways.data
        sel = sa.select([w.c.name, w.c.intnames,
                         ST_LineMerge(ST_Collect(w.c.geom.ST_Transform(4326))).label('geom')])\
                .where(w.c.id == ws.c.child)\
                .where(ws.c.id == oid)\
                .group_by(w.c.name, w.c.intnames)
        return cherrypy.request.db.execute(sel).first()

    @cherrypy.expose
    @cherrypy.tools.gzip(mime_types=['application/gpx+xml'])
    def gpx(self, oid, **params):
        return self.create_gpx_response(oid, self.export(oid))

    @cherrypy.expose
    @cherrypy.tools.gzip(mime_types=['application/vnd.google-earth.kml+xml'])
    def kml(self, oid, **params):
        return self.create_kml_response(oid, self.export(oid))


    @cherrypy.expose
    @cherrypy.tools.gzip(mime_types=['text/json'])
    def geometry(self, oid, factor=None, **params):
        w = cherrypy.request.app.config['DB']['map'].tables.ways.data
        ws = cherrypy.request.app.config['DB']['map'].tables.joined_ways.data
        field = sa.func.ST_Collect(w.c.geom)
        if factor is not None:
            field = w.c.geom.ST_Simplify(field.ST_NPoints()/int(factor))

        sel = sa.select([field.ST_AsGeoJSON()])\
                .where(w.c.id == ws.c.child)\
                .where(ws.c.id == oid)

        res = cherrypy.request.db.execute(sel).first()

        return self.create_geometry_response(res)


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def elevation(self, oid, segments=None, **params):
        raise cherrypy.NotFound()
