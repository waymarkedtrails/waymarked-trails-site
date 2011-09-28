from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from django.conf import settings
import re
import os


subpageexp = re.compile(".. subpage::\s+(\S+)\s+(.*)")

def helppage_view(request, source='', page=None, template="docpage.html"):
    try:
        fdesc = open(settings._BASEDIR + source + '.' 
                   + request.LANGUAGE_CODE + '.rst')
    except IOError:
        fdesc = open(settings._BASEDIR + source + '.en.rst')
            
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
             'content' : docfile
           }

    return direct_to_template(request, 
                              template=template,
                              extra_context=context)


def osmc_symbol_legende(request):
    context = {}
    for path in ('foreground', 'background'): 
        context[path] = []
        for t in os.walk(settings.HIKING_SYMBOL_PATH + '/' + path):
            for fn in t[2]:
                if fn.endswith('.png') and not fn.startswith('empty'):
                    context[path].append(fn[:-4])
        context[path].sort()

    return direct_to_template(request, 
                              template="osmc_symbols.html", 
                              extra_context=context)


    


