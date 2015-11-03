
import sqlalchemy as sa
from sqlalchemy.engine.url import URL
import cherrypy

# Plugin and tool classes borrowed from
# http://www.defuze.org/archives/222-integrating-sqlalchemy-into-a-cherrypy-application.html

class SAEnginePlugin(cherrypy.process.plugins.SimplePlugin):
    def __init__(self, bus, config):
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

def add_language():
    lang = cherrypy.request.headers['Accept-Language']
    llist = []
    for entry in lang.split(','):
        idx = entry.find(';')
        if idx < 0:
            w = 1.0
        else:
            try:
                w = float(entry[idx+3:])
            except ValueError:
                w = 0.0
        llist.append((entry[:idx], w))
    llist.sort(key=lambda x: x[1])
    llist.append(('en', 0.0))
    cherrypy.request.lang_list = tuple([x[0] for x in llist])

cherrypy.tools.add_language = cherrypy.Tool('before_handler', add_language)
