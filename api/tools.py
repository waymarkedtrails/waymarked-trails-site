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

from os import listdir
import os.path
import sqlalchemy as sa
from sqlalchemy.engine.url import URL
import cherrypy
from babel.core import UnknownLocaleError
from babel.support import Translations
from gettext import NullTranslations
from jinja2 import Environment, PackageLoader
import config.defaults as config

# Plugin and tool classes borrowed from
# http://www.defuze.org/archives/222-integrating-sqlalchemy-into-a-cherrypy-application.html

class SAEnginePlugin(cherrypy.process.plugins.SimplePlugin):
    def __init__(self, bus):
        """
        The plugin is registered to the CherryPy engine and therefore
        is part of the bus (the engine *is* a bus) registery.
 
        We use this plugin to create the SA engine. At the same time,
        when the plugin starts we create the tables into the database
        using the mapped class of the global metadata.
 
        Finally we create a new 'bind' channel that the SA tool
        will use to map a session to the SA engine at request time.
        """
        cherrypy.process.plugins.SimplePlugin.__init__(self, bus)
        self.sa_engine = None
        self.db_params = { 'username' : config.DB_USER,
                           'database' : config.DB_NAME,
                           'password' : config.DB_PASSWORD
                         }
 
    def start(self):
        dba = URL('postgresql', **self.db_params)
        self.sa_engine = sa.create_engine(dba, echo=False)
        cherrypy.engine.subscribe('start_thread', self.db_connect)
 
    def stop(self):
        if self.sa_engine:
            self.sa_engine.dispose()
            self.sa_engine = None
 
    def db_connect(self, thread_index):
        cherrypy.thread_data.conn = self.sa_engine.connect()
 
class SATool(cherrypy.Tool):
    def __init__(self):
        """
        The SA tool is responsible for associating a SA session
        to the SA engine and attaching it to the current request.
        Since we are running in a multithreaded application,
        we use the scoped_session that will create a session
        on a per thread basis so that you don't worry about
        concurrency on the session object itself.
 
        This tools binds a session to the engine each time
        a requests starts and commits/rollbacks whenever
        the request terminates.
        """
        cherrypy.Tool.__init__(self, 'on_start_resource',
                               self.bind_session,
                               priority=20)
 
 
    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('on_end_resource',
                                      self.commit_transaction,
                                      priority=80)
 
    def bind_session(self):
        cherrypy.request.db = cherrypy.thread_data.conn
        cherrypy.request.transaction = cherrypy.thread_data.conn.begin()
 
    def commit_transaction(self):
        try:
            cherrypy.request.transaction.commit()
        except:
            cherrypy.request.transaction.rollback()
            raise
        cherrypy.request.db = None



class I18nTool(cherrypy.Tool):
    """
    Tool to create a language list and add babel support.
    """
    def __init__(self):
        self._name = 'I18nTool'
        self._point = 'before_handler'
        self.callable = self.add_language
        self._priority = 100

        self.babel_envs = { 'en' : NullTranslations()}
        self.template_envs = {}
        self.add_template_env('en')

        for name in listdir(config.LOCALE_DIR):
            if os.path.isdir(os.path.join(config.LOCALE_DIR, name, 'LC_MESSAGES')):
                self.babel_envs[name] = None
                self.template_envs[name] = None


    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('before_finalize', self.add_language)

    def add_language(self):
        if 'lang' in cherrypy.request.params:
            cherrypy.request.locales = (cherrypy.request.params['lang'], )
            del cherrypy.request.params['lang']
        else:
            lang = cherrypy.request.headers.get('Accept-Language', '')
            llist = []
            for entry in lang.split(','):
                idx = entry.find(';')
                if idx < 0:
                    llist.append((entry, 1.0))
                else:
                    try:
                        w = float(entry[idx+3:])
                    except ValueError:
                        w = 0.0
                    llist.append((entry[:idx], w))
            llist.sort(key=lambda x: -x[1])
            llist.append(('en', 0.0))
            cherrypy.request.locales = tuple([x[0] for x in llist])

        self.load_translation()

    def load_translation(self):
        for lang in cherrypy.request.locales:
            if lang in self.babel_envs:
                if self.babel_envs[lang] is None:
                    try:
                        self.babel_envs[lang] = Translations.load(config.LOCALE_DIR, lang, 'django')
                    except UnknownLocaleError:
                        del self.babel_envs[lang]
                        continue
                    self.add_template_env(lang)
                cherrypy.request.i18n = self.babel_envs[lang]
                cherrypy.request.templates = self.template_envs[lang]

                return

        cherrypy.request.i18n = self.babel_envs['en']
        cherrypy.request.templates = self.template_envs['en']


    def add_template_env(self, lang):
        self.template_envs[lang] = Environment(loader=PackageLoader('frontend', 'templates'),
                                               extensions=['jinja2.ext.i18n'])
        self.template_envs[lang].install_gettext_translations(self.babel_envs[lang])

cherrypy.tools.I18nTool = I18nTool()
