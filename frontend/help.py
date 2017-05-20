# This file is part of waymarkedtrails.org
# Copyright (C) 2015 Sarah Hoffmann
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

import cherrypy
import yaml
import re
import codecs
import os

import config.defaults as config

imageexp = re.compile("!\[(.*?)\]\((.*?)\)")

@cherrypy.tools.expires(secs=604800, force=True)
class Helppages(object):

    def __init__(self):
        self.helpsrc = None

    def _get_src(self):
        if self.helpsrc is None:
            pagedesc = cherrypy.request.app.config['Site']['help']
            with codecs.open(pagedesc['source'] % 'qot', 'rb', 'utf-8') as helpfd:
                self.helpsrc = yaml.safe_load(helpfd)

        return self.helpsrc

    def _cp_dispatch(self, vpath):
        path = []
        while vpath:
            path.append(vpath.pop())
        path.reverse()
        cherrypy.request.params['path'] = path
        return self

    @cherrypy.expose
    def index(self, **params):
        path = cherrypy.request.params.get('path', ('about',))
        menu, outpage = self._load_menu(path)
        gconf = cherrypy.request.app.config.get('Global')

        if outpage is None:
            if len(path) == 2 and path[1] == 'osmc_legende':
                return self.osmc_legende(menu)
            # ups, requested section does not exist
            _ = cherrypy.request.i18n.gettext
            outpage = (_('Error'), _('The requested page does not exist.'))
        elif path[0] == 'contact' and 'IMPRESSUM' in gconf:
            outpage[1] += "\n\nImpressum\n---------\n"
            outpage[1] += gconf["IMPRESSUM"]

        # add the path to image URLs
        # XXX currently hardcoded to settings.MEDIA_URL/img
        outtext = imageexp.sub("![\g<1>](%s/img/\g<2>)" % config.MEDIA_URL, outpage[1])

        context = {'menu' : menu,
                   'title' : outpage[0],
                   'content' : outtext,
                   'g' : gconf,
                   'l' : cherrypy.request.app.config.get('Site')}

        return cherrypy.request.templates.get_template('help.html').render(**context)


    def osmc_legende(self, menu):
        context = {'menu' : menu}
        for path in ('foreground', 'background'): 
            context[path] = []
            for t in os.walk(os.path.join(config.OSMC_EXAMPLE_PATH, path)):
                for fn in t[2]:
                    if fn.endswith('.png') and not fn.startswith('empty'):
                        context[path].append(fn[:-4])
            context[path].sort()
        context['g'] = cherrypy.request.app.config.get('Global')
        context['l'] = cherrypy.request.app.config.get('Site')

        return cherrypy.request.templates.get_template('osmc_symbol.html').render(**context)


    def _load_menu(self, page):
        pagedesc = cherrypy.request.app.config['Site']['help']
        helpsrc = self._get_src()
        for lang in cherrypy.request.locales:
            if lang == 'en':
                break
            try:
                with codecs.open(pagedesc['source'] % lang, 'rb', 'utf-8') as helpfd:
                     helpsrc = self._merge_yaml(yaml.safe_load(helpfd), helpsrc)
            except IOError:
                continue # ignored, go to full fallback
            break

        menu = []
        outpage = self._buildmenu('', menu, pagedesc['structure'], helpsrc, page)
        return menu, outpage

    def _merge_yaml(self, prim, sec):
        for k in sec:
            if k in prim:
                if not isinstance(sec[k], str):
                    prim[k] = self._merge_yaml(prim[k], sec[k])
            else:
                prim[k] = sec[k]
        return prim

    def _buildmenu(self, urlprefix, menu, menustruct, helpsrc, pageparts):
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
                        subout = self._buildmenu(newurlprefix, menu, parts, helpsrc, newpageparts)
                        if subout:
                            outstr = subout
                        menu.append('/SUBMENU')
            else:
                print("WARNING: the following page is missing:", pageid)

        return outstr


