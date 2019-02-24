# This file is part of waymarkedtrails.org
# Copyright (C) 2015 Sarah Hoffmann
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
from tempfile import NamedTemporaryFile
import cherrypy
from datetime import datetime as dt
import sqlalchemy as sa

import api.details
import api.listings
import api.guidepost
from api.vector_tiles import TilesApi

from osgende.common.tags import TagStore

@cherrypy.tools.db()
@cherrypy.tools.expires(secs=21600, force=True)
class RoutesApi(object):

    def __init__(self, mapdb, maptype):
        # sub-directories
        if maptype == 'routes':
            self.list = api.listings.RouteLists()
            self.details = RouteDetails(mapdb)
            self.tiles = TilesApi()
        elif maptype == 'slopes':
            self.list = api.listings.SlopeLists()
            self.details = SlopeDetails()

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/help")

    @cherrypy.expose
    def last_update(self):
        status = cherrypy.request.app.config['DB']['map'].osmdata.status
        mtype = cherrypy.request.app.config['Global']['BASENAME']
        sel = sa.select([status.c.date]).where(status.c.part == mtype)
        date = cherrypy.request.db.scalar(sel)

        return date.isoformat() if date is not None else (dt.utcnow().isoformat() + 'Z')

    @cherrypy.expose
    def symbols(self, **params):
        from db.common.symbols import ShieldFactory
        factory = ShieldFactory(
            'SwissMobile',
            'JelRef',
            'KCTRef',
            'ItalianHikingRefs',
            'OSMCSymbol',
            'Nordic',
            'Slopes',
            'ShieldImage',
            'TextColorBelow',
            'ColorBox',
            'TextSymbol',
        )

        sym = factory.create(TagStore(params), params.get('_network', ''), 10)

        if sym is None:
            raise cherrypy.NotFound()

        with NamedTemporaryFile() as f:
            sym.write_image(f.name)
            factory._mangle_svg(f.name)

            with open(f.name, 'rb') as f:
                res = f.read()

        cherrypy.response.headers['Content-Type'] = 'image/svg+xml'
        return res


class RouteDetails(object):

    def __init__(self, mapdb):
        self.relation = api.details.RelationInfo('level')
        if hasattr(mapdb.tables, 'guideposts'):
            self.guidepost = api.guidepost.GuidepostInfo()

class SlopeDetails(object):

    def __init__(self):
        self.relation = api.details.RelationInfo('piste')
        self.way = api.details.WayInfo('piste')
        self.wayset = api.details.WaySetInfo('piste')
