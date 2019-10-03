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
import cherrypy
import sqlalchemy as sa

from osgende.common.tags import TagStore

@cherrypy.popargs('oid')
class GuidepostInfo(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip(mime_types=['application/json'])
    def index(self, oid, **params):
        cfg = cherrypy.request.app.config
        mapdb = cfg['DB']['map']

        r = mapdb.tables.guideposts.data
        o = mapdb.osmdata.node.data

        sel = sa.select([r.c.name, r.c.ele,
                         r.c.geom.ST_X().label('lon'),
                         r.c.geom.ST_Y().label('lat'),
                         o.c.tags])\
                .where(r.c.id == oid)\
                .where(o.c.id == oid)

        res = cherrypy.request.db.execute(sel).first()

        if res is None:
            raise cherrypy.NotFound()

        ret = OrderedDict()
        loctags = TagStore.make_localized(res['tags'], cherrypy.request.locales)
        ret['type'] = 'guidepost'
        ret['id'] = oid
        if 'name' in loctags:
            ret['name'] = loctags['name']
            if res['name']  and res['name'] != ret['name']:
                ret['local_name'] = res['name']
        if res['ele'] is not None:
            ret['ele'] = loctags.get_length('ele', unit='m', default='m')
        for tag in ('ref', 'operator', 'description', 'note'):
            if tag in loctags:
                ret[tag] = loctags[tag]
        if 'image' in loctags:
            imgurl = loctags['image']
            if imgurl.startswith('http://') or imgurl.startswith('https://'):
                ret['image'] = imgurl
        ret['tags'] = res['tags']
        ret['y'] = res['lat']
        ret['x'] = res['lon']

        return ret

