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

def convertToInt(val, maxval, default):
    if val is not None:
        res = val
        try:
            res = min(maxval, int(res))
        except:
            res = default
    else:
        res = default
    return res
 
def search(request, manager):
    if 'term' not in request.GET:
        return direct_to_template(request, 'search/noresults.html')
    term = request.GET['term']
    maxresults = convertToInt(request.GET.get('maxresults'), 100, 10)
    moreresults = convertToInt(request.GET.get('moreresults'), 
                                  100, min(100, maxresults+10))

    objs = []
    # First try: exact match of ref
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


    if len(objs) > maxresults:
        objs = objs[:-1]
    else:
        moreresults = 0
    extra_context = { 'searchterm' : term,
                      'objs' : objs,
                      'moreresults' : moreresults,
                      'symbolpath' : settings.ROUTEMAP_COMPILED_SYMBOL_PATH}
    return direct_to_template(request, 'search/result.html',
                              extra_context)

def place_search(request, manager):
    if 'term' not in request.GET:
        return direct_to_template(request, 'search/noresults.html')
    term = request.GET['term']
    maxresults = convertToInt(request.GET.get('maxresults'), 100, 10)

    url = "%s?q=%s&format=json" % (settings.ROUTEMAP_NOMINATIM_URL,
                                   urllib2.quote(term))
    try:
        req = urllib2.Request(url, headers={
                'User-Agent' : 'Python-urllib/2.7 Routemaps(report problems to admin@lonvia.de)'
                })
        data = urllib2.urlopen(req).read()
        data = json.loads(data)
    except:
        return direct_to_template(request, 'search/noresults.html')

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
            if len(objs) >= maxresults:
                break

    extra_context = { 'searchterm' : term,
                      'objs' : objs}
    return direct_to_template(request, 'search/places.html',
                              extra_context)
