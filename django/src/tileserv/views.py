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

from django.http import Http404, HttpResponse
from django.conf import settings

def png_tile(request, table, zoom, tilex, tiley):
    tilex = int(tilex)
    tiley = int(tiley)
    zoom = int(zoom)

    if zoom > settings.TILE_MAXZOOM:
        raise Http404

    return HttpResponse(table.tiles.get_image(zoom, tilex, tiley), 
                        mimetype="image/png")
