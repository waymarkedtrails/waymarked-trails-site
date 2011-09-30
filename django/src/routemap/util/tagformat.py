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

"""
Helper functions to format the OSM tag values.
"""

import re

unit_re = re.compile("\s*(\d+)([.,](\d+))?\s*([a-zA-Z]*)")

def convert_to_km(value):
    """Take an OSM value and make the best guess at a
       conversion into kilometers.
    """
    if value is not None:
        m = unit_re.match(value)
        if m is not None:
            if m.group(3) is None:
                mag = float(m.group(1))
            else:
                mag = float('%s.%s' % (m.group(1), m.group(3)))
            unit = m.group(4).lower()
            if unit == '' or unit == 'km':
                return mag
            elif unit == 'm':
                return mag/1000
            elif unit == 'mi':
                return mag*1.6093

    return None
