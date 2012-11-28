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

from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from django.conf import settings
import re
import os
import yaml


imageexp = re.compile("!\[(.*?)\]\((.*?)\)")

def showpage(request, page=None, template="docpage.html"):
    pagedesc = settings.ROUTEMAP_HELPPAGES
    helpfd = open(pagedesc['source'] % 'qot')
    helpsrc = yaml.safe_load(helpfd)
    helpfd.close()
    try:
        helpfd = open(pagedesc['source'] % request.LANGUAGE_CODE)
        helpsrc = _merge_yaml(yaml.safe_load(helpfd), helpsrc)
        helpfd.close()
    except IOError:
        pass # ignored, go to full fallback    
    
    menu = []
    pageparts = page.split('/')
    outpage = _buildmenu('', menu, pagedesc['structure'], helpsrc, pageparts)

    if outpage is None:
        # ups, requested section does not exist
        outpage = (_('Error'), _('The requested page does not exist.'))

    # add the path to image URLs
    # XXX currently hardcoded to settings.MEDIA_URL/img
    outtext = imageexp.sub("![\g<1>](%s/img/\g<2>)" % settings.MEDIA_URL, outpage[1])

    context = {'menu' : menu, 'title' : outpage[0], 'content' : outtext}

    return direct_to_template(request, 
                              template=template,
                              extra_context=context)

def _merge_yaml(prim, sec):
    for k in sec:
        if k in prim:
            if not isinstance(sec[k],basestring):
                prim[k] = _merge_yaml(prim[k], sec[k])
        else:
            prim[k] = sec[k]
    return prim

def _buildmenu(urlprefix, menu, menustruct, helpsrc, pageparts):
    outstr = None

    for item in menustruct:
        pageid = item[0]
        if pageid in helpsrc:
            dooutput = False
            srcpage = helpsrc[pageid]
            newpageparts = None
            if pageparts and pageid == pageparts[0]:
                if len(pageparts) == 1:
                    outstr = [srcpage['title'], '']
                    dooutput = True
                else:
                    newpageparts = pageparts[1:]
            if urlprefix:
                newurlprefix = urlprefix + '/' + pageid
            else:
                newurlprefix = pageid
            menu.append((newurlprefix, srcpage['title']))
            for parts in item[1:]:
                if isinstance(parts, str):
                    if dooutput:
                        outstr[1] += srcpage[parts]
                        outstr[1] += '\n\n'
                else:
                    menu.append('SUBMENU')
                    subout = _buildmenu(newurlprefix, menu, parts, helpsrc, newpageparts)
                    if subout:
                        outstr = subout
                    menu.append('/SUBMENU')
        else:
            print "WARNING: the following page is missing:", pageid


    return outstr


def osmc_symbol_legende(request, template="osmc_symbols.html"):
    context = {}
    for path in ('foreground', 'background'): 
        context[path] = []
        for t in os.walk(os.path.join(settings.ROUTEMAP_SOURCE_SYMBOL_PATH, path)):
            for fn in t[2]:
                if fn.endswith('.png') and not fn.startswith('empty'):
                    context[path].append(fn[:-4])
        context[path].sort()

    return direct_to_template(request, 
                              template=template, 
                              extra_context=context)


    


