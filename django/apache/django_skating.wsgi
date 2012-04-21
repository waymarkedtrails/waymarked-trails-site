import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'routemap.skating.settings'

sys.path.append('/home/suzuki/osm/dev/multiroutemap/django/src')
sys.path.append('/home/suzuki/osm/dev/multiroutemap/django/contrib')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

