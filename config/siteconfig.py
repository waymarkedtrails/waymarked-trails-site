# -*- coding: utf-8 -*-
# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2011-2012 Sarah Hoffmann
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
"""
Common settings, used for all the route maps.

You can define your own local settings in settings_local.py to prevent
conflict when updating Waymarked Trails.
"""

from os import environ as osenv

DEBUG = True
TEMPLATE_DEBUG = DEBUG


# The first admin address will be used as contact address when sending
# requests to other servers.
# Word of warning: If no address is provided, these requests will simply
# not work.
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS
SECRET_KEY = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'planet',                      # Or path to database file if using sqlite3.
        'USER': 'osm',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'SRID' : '900913',
        'OPTIONS' : {
            'autocommit' : True
        },
    }
}

# base URL for search engine
ROUTEMAP_NOMINATIM_URL = 'http://nominatim.openstreetmap.org/search'

# base URL for tile serving
ROUTEMAP_TILE_BASEURL = 'http://tile.waymarkedtrails.org'

# number of results to list in route browser
ROUTEMAP_MAX_ROUTES_IN_LIST = 30

ROUTEMAP_PAGEINFO = {}

#############################################################################
#
# Directories

import os.path as op
PROJECTDIR =  op.normpath(op.join(op.realpath(__file__), '../..')) + '/'

# Cache location set to file
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/waymarkedtrails-cache',
    }
}

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = PROJECTDIR + 'static/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/static/'

ROUTEMAP_SOURCE_SYMBOL_PATH = PROJECTDIR + 'static/img/symbols'
ROUTEMAP_UPDATE_TIMESTAMP = PROJECTDIR + 'last_update'

#############################################################################
#
# Elevation profiles

SHOW_ELEV_PROFILE =  False
ELEVATION_PROFILE_DEM = PROJECTDIR + 'static/elevationdem/DEM.vrt'
ELEVATION_ACCURACY = 15
ELEVATION_ROUNDING = 5

#############################################################################
#
# Locale settings

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Etc/UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

# Default formatting for datetime objects. See all available format strings here:
# http://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
# use ISO 8601 format, avoiding English words and formatting in unsupported languages
DATETIME_FORMAT = 'Y-m-d, H:i'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

LOCALE_PATHS = ( PROJECTDIR + 'django/locale', )

# Available interface translations. Listed alphabetically (by you) by language self name. 
# Non-latin charset names listed as if transliterated to latin script.
LANGUAGES = (
  ('ar', 'العربية'),	# Transliterates to "al'erebyh" at http://mylanguages.org/arabic_romanization.php
  ('ast', 'Asturianu'),
  ('az', 'Azərbaycanca'),
  ('id', 'Bahasa Indonesia'),
  ('ms', 'Bahasa Melayu'),
  ('br', 'Brezhoneg'),
  ('bxr', 'Буряад'),  # Transliterates to "Buryaad"
  ('ca', 'Català'),
  ('cs', 'Česky'),  
  ('da', 'Dansk'),
  ('de', 'Deutsch'),
  ('en', 'English'),
  ('es', 'Español'),
  ('eo', 'Esperanto'),
  ('fo', 'Føroyskt'),
  ('fr', 'Français'),
  ('gl', 'Galego'),
  ('ko', '한국어'),  # Transliterates to "han-gu-geo" at http://sori.org/hangul/conv2kr.cgi
  ('ia', 'Interlingua'),
  ('is', 'Íslenska'),
  ('it', 'Italiano'),
  ('he', 'עברית'), # Hebrew, transliterates to "Ivrit" accroding to wikipedia
  ('hu', 'Magyar'),
  ('mk', 'Македонски'),  # Transliterates to "Makedonski" (http://translit.cc/)
  ('nl', 'Nederlands'),  
  ('ja', '日本語'),      # Transliterates to "Nihongo"
  ('nb', 'Norsk (bokmål)'),
  ('nn', 'Norsk (nynorsk)'),
  ('pfl', 'Pälzisch'),
  ('pl', 'Polski'),
  ('pt', 'Português'),
  ('pt-br', 'Português do Brasil'),
  ('ksh', 'Ripoarisch'),
  ('ro', 'Română'),
  ('ru', 'Русский'),    # Transliterates to "Russkij" (http://translit.cc/)
  ('fi', 'Suomi'),
  ('sl', 'Slovenščina'),
  ('sr-el', 'Serbian'),
  ('sr-ec', 'српски'),  # Transliterates to "srpski" (http://translit.cc/)
  ('sv', 'Svenska'),
  ('tl', 'Tagalog'),
  ('vi', 'Tiếng Việt'),
  ('tly', 'толышә зывон'), # Transliterates to "Tolishe zivon"
  ('tr', 'Türkçe'),
  ('uk', 'українська'),    # Transliterates to 'ukrayins"ka' (http://translit.cc/)
  ('vec', 'Vèneto'),
  ('diq', 'Zazaki'),
  ('zh-cn', '中文(简体)'), # Transliterates to "Zhōngwén"
  ('no', ''), # Unspecified Norwegian. Points to "nb".
)

# Language aliases for languages where specific and general versions
# exist. Note that this should not be used to create fallbacks.
# Each alias gets a weight between 0.0 and 1.0.
LANGUAGE_ALIAS = {
  'no': (('nb', 1.0),('nn', 0.9)),
  'nb': (('no', 1.0),),
  'nn': (('no', 1.0),),
}

#############################################################################
#
# Django modules

ROOT_URLCONF = 'routemap.sites.urls'

TEMPLATE_LOADERS = (
    'django_mobile.loader.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_mobile.middleware.MobileDetectionMiddleware',
    'django_mobile.middleware.SetFlavourMiddleware'
)

TEMPLATE_DIRS = (
    PROJECTDIR + "django/templates"
)

TEMPLATE_CONTEXT_PROCESSORS = (
     'django.core.context_processors.request',
     'django.core.context_processors.i18n',
     'django.core.context_processors.media',
     'routemap.util.context_processors.pageinfo',
     'django_mobile.context_processors.flavour'
     )

INSTALLED_APPS = (
     'django.contrib.markup',
     'routemap',
     'django_mobile',
     'django_assets',
)

ASSETS_DEBUG = DEBUG
ASSETS_AUTO_BUILD = False


#############################################################################
#
# Local settings

try:
    from siteconfig_local import *
except ImportError:
    pass # no local settings provided

