# This file is part of Lonvia's Hiking Map
# Copyright (C) 2011 Sarah Hoffmann
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
"""Tables storing information about guideposts and other nodes.
"""

import re

from osgende import NodeSubTable
from osgende.common.postgisconn import PGTable
import conf

class GuidePosts(NodeSubTable):
    """Information about the guideposts.
    """
    elepattern = re.compile('[\\d.]+')

    def __init__(self, db):
        NodeSubTable.__init__(
                self, db, conf.DB_GUIDEPOST_TABLE,
                conf.TAGS_GUIDEPOST_SUBSET,
                transform='ST_Transform(%s, 900913)')

    def create(self):
        PGTable.create(self,
            """(id        bigint PRIMARY KEY,
                name      text,
                ele       text
                )""")
        self.add_geometry_column("geom", "900913", 'POINT', with_index=True)

    def transform_tags(self, osmid, tags):
        outtags = { 'name' : tags.get('name') }
        if 'ele'in tags:
            m = self.elepattern.search(tags['ele'])
            if m:
                outtags['ele'] = m.group(0)
            # XXX check for ft

        return outtags

class NetworkNodes(NodeSubTable):
    """Information about the guideposts.
    """

    def __init__(self, db):
        NodeSubTable.__init__(
                self, db, conf.DB_NETWORKNODE_TABLE,
                conf.TAGS_NETWORKNODE_SUBSET,
                transform='ST_Transform(%s, 900913)')

    def create(self):
        PGTable.create(self,
            """(id        bigint PRIMARY KEY,
                name      text
               )""")
        self.add_geometry_column("geom", "900913", 'POINT', with_index=True)

    def transform_tags(self, osmid, tags):
        return { 'name' : tags.get('rwn_ref') }
