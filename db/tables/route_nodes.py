# This file is part of the Waymarked Trails Map Project
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
""" Various tables for nodes in a route network.
"""

from re import compile as re_compile

import sqlalchemy as sa
from geoalchemy2 import Geometry

from osgende.generic import TransformedTable
from osgende.common.tags import TagStore
from db.configs import GuidePostConfig, NetworkNodeConfig
from db import conf


GUIDEPOST_CONF = conf.get('GUIDEPOSTS', GuidePostConfig)

class GuidePosts(TransformedTable):
    """ Information about guide posts. """
    elepattern = re_compile('[\\d.]+')

    def __init__(self, meta, source):
        self.srid = meta.info.get('srid', source.c.geom.type.srid)
        super().__init__(meta, GUIDEPOST_CONF.table_name, source)

    def add_columns(self, table, src):
        table.append_column(sa.Column('name', sa.String))
        table.append_column(sa.Column('ele', sa.String))
        table.append_column(sa.Column('geom', Geometry('POINT', srid=self.srid)))

    def transform(self, obj):
        tags = TagStore(obj['tags'])
        # filter by subtype
        if GUIDEPOST_CONF.subtype is not None:
            booltags = tags.get_booleans()
            if len(booltags) > 0:
                if not booltags.get(GUIDEPOST_CONF.subtype, False):
                    return None
            else:
                if GUIDEPOST_CONF.require_subtype:
                    return None

        outtags = { 'name' : tags.get('name'), 'ele' : None }
        if 'ele'in tags:
            m = self.elepattern.search(tags['ele'])
            if m:
                outtags['ele'] = m.group(0)
            # XXX check for ft

        if self.srid == self.src.c.geom.type.srid:
            outtags['geom'] = obj['geom']
        else:
            outtags['geom'] = obj['geom'].ST_Transform(self.srid)

        return outtags


NETWORKNODE_CONF = conf.get('NETWORKNODES', NetworkNodeConfig)

class NetworkNodes(TransformedTable):
    """ Information about referenced nodes in a route network.
    """

    def __init__(self, meta, source):
        self.srid = meta.info.get('srid', source.c.geom.type.srid)
        super().__init__(meta, NETWORKNODE_CONF.table_name, source)

    def add_columns(self, table, src):
        table.append_column(sa.Column('name', sa.String))
        table.append_column(sa.Column('geom', Geometry('POINT', srid=self.srid)))

    def transform(self, obj):
        tags = TagStore(obj['tags'])

        if NETWORKNODE_CONF.node_tag not in tags:
            return None

        outtags = { 'name' : tags[NETWORKNODE_CONF.node_tag] }

        if self.srid == self.src.c.geom.type.srid:
            outtags['geom'] = obj['geom']
        else:
            outtags['geom'] = obj['geom'].ST_Transform(self.srid)

        return outtags
