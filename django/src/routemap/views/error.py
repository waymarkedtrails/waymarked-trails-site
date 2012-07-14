# -*- coding: utf-8 -*-
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

# common settings for all route maps
from django.conf import settings

from django.template import RequestContext, loader
from django import http

def handler404(request):
    t = loader.get_template('404.html')
    return http.HttpResponseNotFound(t.render(RequestContext(request, 
      settings.ROUTEMAP_PAGEINFO)))

def handler500(request):
    t = loader.get_template('500.html')
    return http.HttpResponseNotFound(t.render(RequestContext(request, 
      settings.ROUTEMAP_PAGEINFO)))
