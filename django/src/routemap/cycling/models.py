# This file is part of Lonvia's Route Maps Project
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

from django.contrib.gis.db import models
import routemap.common.routemodels

class CyclingRoutes(routemap.common.routemodels.RouteTableModel):
    """Table with information about cycling routes.
    """
    
    symbol = models.TextField(null=True)
    level = models.IntegerField()
    top = models.BooleanField()

    objects = models.GeoManager()

    class Meta:
        db_table = u'routes'
        db_tablespace = u'cycling'


