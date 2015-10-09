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

from sqlalchemy import Column, String
from osgende.nodes import NodeSubTable
from db import conf


class GuidePostConfig:
    table_name = 'guideposts'
    node_subset = "tags @> 'tourism=>information, information=>guidepost'::hstore"
    subtype = None
    require_subtype = False

GUIDEPOST_CONF = conf.get('GUIDEPOSTS', GuidePostConfig)

class GuidePosts(NodeSubTable):
    """ Information about guide posts. """
    elepattern = re_compile('[\\d.]+')

    def __init__(self, meta, osmdata, geom_change=None):
        super().__init__(meta, GUIDEPOST_CONF.table_name, osmdata,
                         subset=GUIDEPOST_CONF.node_subset,
                         geom_change=geom_change)

    def columns(self):
        return (Column('name', String),
                Column('ele', String)
               )

    def transform_tags(self, osmid, tags):
        # filter by subtype
        if GUIDEPOST_CONF.subtype is not None:
            booltags = tags.get_booleans()
            if len(booltags) > 0:
                if not booltags.get(GUIDEPOST_CONF.subtype, False):
                    return None
            else:
                if GUIDEPOST_CONF.require_subtype:
                    return None

        outtags = { 'name' : tags.get('name') }
        if 'ele'in tags:
            m = self.elepattern.search(tags['ele'])
            if m:
                outtags['ele'] = m.group(0)
            # XXX check for ft

        return outtags


class NetworkNodeConfig:
    table_name = 'networknodes'
    node_tag = 'ref'

NETWORKNODE_CONF = conf.get('NETWORKNODES', NetworkNodeConfig)

class NetworkNodes(NodeSubTable):
    """ Information about referenced nodes in a route network.
    """

    def __init__(self, meta, osmdata, geom_change=None):
        super().__init__(meta, NETWORKNODE_CONF.table_name, osmdata,
                         subset=text('tags ? %s' % NETWORKNODE_CONF.node_tag),
                         geom_change=geom_change)

    def columns(self):
        return (Column('name', String),)

    def transform_tags(self, osmid, tags):
        return { 'name' : tags.get(NETWORKNODE_CONF.node_tag) }
