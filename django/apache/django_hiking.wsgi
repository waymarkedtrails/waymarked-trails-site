import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'hiking.settings'

sys.path.append('/home/suzuki/osm/dev/hikingmap/django/src')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

