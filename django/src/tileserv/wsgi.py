import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tileserv.settings")

sys.path.append(os.path.normpath(os.path.join(os.path.realpath(__file__), '../..')))
sys.path.append(os.path.normpath(os.path.join(os.path.realpath(__file__), '../../../../config')))


# This application object is used by the development server
# as well as any WSGI server configured to use this file.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
