import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'routemap.skating.settings'

basepath = os.path.normpath(os.path.join(os.path.realpath(__file__), '../..'))
sys.path.append(os.path.join(basepath, 'src'))
sys.path.append(os.path.join(basepath, 'contrib'))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

