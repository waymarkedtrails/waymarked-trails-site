import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'cycling.settings'

sys.path.append('/home/suzuki/osm/dev/cyclingmap/django/src')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

