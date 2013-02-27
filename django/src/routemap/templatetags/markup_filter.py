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

import re

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def filterpara(value):
    """ Remove paragraph markers.
    """
    if value.startswith('<p>') and value.endswith('</p>'):
        return value[3:-4];
    return value
filterpara.is_safe = True

@register.filter
def prefixurl(value, arg):
    """ Prefix all links with the given prefix.
    """
    return re.sub('(href=["\'])', '\\1' + arg, value)
prefixurl.is_safe = True
