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
from django.views.generic.simple import direct_to_template
from django.conf import settings
import re
import os


subpageexp = re.compile(".. subpage::\s+(\S+)\s+(.*)")

def helppage_view(request, source, page=None, template="docpage.html", pagetitle=None, cssfile=None, bgimage=None):
    try:
        fdesc = open(source + '.' 
                   + request.LANGUAGE_CODE + '.rst')
    except IOError:
        fdesc = open(source + '.en.rst')
            
    docfile = ''
    menu = []
    curlevel = 1
    inpage = False
    title = None
    for line in fdesc:
        m = subpageexp.match(line)
        if m is not None:
            inpage = (m.group(1) == page)
            if inpage:
                title = m.group(2)
            items = len(m.group(1).split('/'))
            newlevel = items
            while items > curlevel:
                menu.append('SUBMENU')
                items -= 1
            while items < curlevel:
                menu.append('/SUBMENU')
                items += 1
            curlevel = newlevel
            menu.append((m.group(1), m.group(2)))
        else:
            if inpage:
                docfile += line
    fdesc.close()

    if title is None:
        # ups, requested section does not exist
        title = _('Error')
        docfile = _('The requested page does not exist')

    context = { 'menu' : menu,
             'title' : title,
             'content' : docfile,
             'pagetitle' : pagetitle,
             'cssfile' : cssfile,
             'bgimage' : bgimage
           }

    return direct_to_template(request, 
                              template=template,
                              extra_context=context)


def osmc_symbol_legende(request, template="osmc_symbols.html"):
    context = {}
    for path in ('foreground', 'background'): 
        context[path] = []
        for t in os.walk(os.apth.join(settings.ROUTEMAP_SOURCE_SYMBOL_PATH, path)):
            for fn in t[2]:
                if fn.endswith('.png') and not fn.startswith('empty'):
                    context[path].append(fn[:-4])
        context[path].sort()

    return direct_to_template(request, 
                              template=template, 
                              extra_context=context)


    


