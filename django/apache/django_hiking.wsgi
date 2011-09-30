import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'routemap.hiking.settings'

sys.path.append('/home/suzuki/osm/dev/multiroutemap/django/src')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

