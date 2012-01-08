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

from django.utils.translation import ugettext as _
from django.conf import settings
from django.views.generic.simple import direct_to_template
import urllib2
import json

def search(request, manager):
    if 'term' not in request.GET:
        return direct_to_template(request, 'search/noresults.html')
    term = request.GET['term']
    maxresults = 10
    # TODO take maxresults from GET
    

    objs = []
    # First try: exact match of ref
    # XXX should be minus spaces
    objs.extend(manager.filter(name='[%s]' % term)[:maxresults+1])

    # Second try: fuzzy matching of text
    if len(objs) <= maxresults:
        numres = maxresults-len(objs) + 1
        qs = manager.extra(
                 select={'sml' : 'similarity(name, %s)',
                         'xmin' : 'ST_XMin(geom)',
                         'xmax' : 'ST_XMax(geom)',
                         'ymin' : 'ST_YMin(geom)',
                         'ymax' : 'ST_YMax(geom)',
                         },
                 select_params=(term,),
                 order_by=['-sml']
             )#.extra(where=('2.0 > 1.0', ))
        objs.extend(qs[:numres])

    if len(objs) == 0:
        return direct_to_template(request, 'search/noresults.html')

    hasmore = len(objs) > maxresults
    if hasmore:
        objs = objs[:-1]
    extra_context = { 'searchterm' : term,
                      'objs' : objs,
                      'hasmore' : hasmore,
                      'symbolpath' : settings.ROUTEMAP_COMPILED_SYMBOL_PATH}
    return direct_to_template(request, 'search/result.html',
                              extra_context)

def place_search(request, manager):
    if 'term' not in request.GET:
        return direct_to_template(request, 'search/noresults.html')
    term = request.GET['term']
    maxresults=10

    url = "http://zephyria/nominatim/search.php?q=%s&format=json" % urllib2.quote(term)
    try:
        data = urllib2.urlopen(url).read()
    except urllib2.URLError:
        return direct_to_template(request, 'search/noresults.html')
    data = json.loads(data)
    print data

    objs = []
    for res in data:
        # sanity checks, never trust an external URL
        if 'display_name' in res and 'boundingbox' in res:
            bbox = res['boundingbox']
            if len(bbox) != 4:
                continue
            try:
                bbox = [float(x) for x in bbox]
            except:
                continue
       
            objs.append({
                'name' : res['display_name'],
                'bbox' : bbox,
                'icon' : res.get('icon', '')
            })
            if len(objs) > maxresults:
                break

    hasmore = len(objs) > maxresults
    if hasmore:
        objs = objs[:maxresults]

    extra_context = { 'searchterm' : term,
                      'objs' : objs,
                      'hasmore' : hasmore}
    print objs
    return direct_to_template(request, 'search/places.html',
                              extra_context)
