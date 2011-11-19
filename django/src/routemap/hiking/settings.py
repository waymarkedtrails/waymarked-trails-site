# This file is part of Lonvia's Route Maps Project
# Copyright (C) 2011 Sarah Hoffmann
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

# Django settings for hiking project.
_ = lambda s : s

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#_BASEDIR = '/secondary/osm/django/'
_BASEDIR = '/home/suzuki/osm/dev/multiroutemap/django/'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'planet',                      # Or path to database file if using sqlite3.
        'USER': 'osm',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS' : {
            'autocommit' : True
        },
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = _BASEDIR + '../static/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/static/'

LANGUAGES = (
  ('en', _('English')),
  ('de', _('German')),
  ('fr', _('French')),
  ('it', _('Italian'))
)

LANGUAGE_CODE = 'en'
LOCALEURL_USE_ACCEPT_LANGUAGE = True
PREFIX_DEFAULT_LOCALE = False

LOCALE_PATHS = ( _BASEDIR + 'locale', )

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'pfy1^7!))-#!ft5_is)5**zn7n$m_hdwa!6ex7)44=r!zxiu4k'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'localeurl.middleware.LocaleURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'routemap.hiking.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    _BASEDIR + "templates"
)

TEMPLATE_CONTEXT_PROCESSORS = (
     #'django.contrib.auth.context_processors.auth',
     #'django.core.context_processors.debug',
     'django.core.context_processors.request',
     'django.core.context_processors.i18n',
     'django.core.context_processors.media',
     #'django.contrib.messages.context_processors.messages'
     )


INSTALLED_APPS = (
     'localeurl',
     'django.contrib.markup',
#    'django.contrib.auth',
#    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#    'django.contrib.sites',
#    'django.contrib.gis',
#    'hiking.osmosis',
)

# Project settings
ROUTEMAP_PAGEINFO = {
    "maptopic" : _("Hiking"),
    "cssfile" : "hiking_theme.css",
    "bgimage" : "banner.jpg",
    "iconimg" : "map_hiking.ico"
}

ROUTEMAP_MAX_ROUTES_IN_LIST = 30
ROUTEMAP_SOURCE_SYMBOL_PATH = _BASEDIR + '../static/img/symbols'
ROUTEMAP_COMPILED_SYMBOL_PATH = 'hikingsyms'
ROUTEMAP_UPDATE_TIMESTAMP = _BASEDIR + '/../last_update'



