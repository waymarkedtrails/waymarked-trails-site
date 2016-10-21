# This file is part of waymarkedtrails.org
# Copyright (C) 2016 Sarah Hoffmann
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

import cherrypy
import api.common
import sqlalchemy as sa
import json
from io import StringIO


# constants for bbox computation for level 12
MAPWIDTH = 20037508.34
TILEWIDTH = MAPWIDTH/(2**11)

@cherrypy.tools.db()
@cherrypy.popargs('zoom', 'x', 'y')
class TilesApi(object):

    @cherrypy.expose
    @cherrypy.tools.response_headers(headers=[('Content-Type', 'text/json')])
    @cherrypy.tools.expires(secs=21600, force=True)
    def index(self, zoom, x, y):
        if zoom != '12':
            raise cherrypy.HTTPError(400, 'Only zoom level 12 available')

        ypt = y.find('.')

        if ypt <= 0 or y[ypt+1:] != 'json':
            raise cherrypy.NotFound()

        x = int(x)
        y = int(y[:ypt])

        if x < 0 or x > 2**12 or y < 0 or y > 2**12:
            raise cherrypy.NotFound()

        b = api.common.Bbox((x * TILEWIDTH - MAPWIDTH,
                             MAPWIDTH - (y + 1) * TILEWIDTH,
                             (x + 1) * TILEWIDTH - MAPWIDTH,
                             MAPWIDTH - y * TILEWIDTH))

        mapdb = cherrypy.request.app.config['DB']['map']
        d = mapdb.tables.style.data

        q = sa.select([d.c.rels, d.c.allshields.label('shields'),
                    d.c.network, d.c.style, d.c['class'],
                    d.c.geom.ST_Intersection(b.as_sql()).ST_AsGeoJSON().label('geom')])\
              .where(d.c.geom.intersects(b.as_sql()))

        out = StringIO()

        out.write("""{ "type": "FeatureCollection",
                        "crs": {"type": "name", "properties": {"name": "EPSG:3857"}},
                        "features": [""")

        sep = ''
        for r in cherrypy.request.db.execute(q):
            out.write(sep)
            out.write('{ "type": "Feature", "geometry":')
            out.write(r['geom'])
            out.write(', "properties" : ')
            json.dump({ 'relations' : r['rels'],
                        'shields' : r['shields'],
                        'network' : r['network'],
                        'style' : r['style'],
                        'class' : r['class']
                      }, out)
            out.write('}')
            sep = ','

        out.write("]}")

        return out.getvalue().encode('utf-8')
