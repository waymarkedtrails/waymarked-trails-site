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

# Django settings, common for all the route maps

DEBUG = True
TEMPLATE_DEBUG = DEBUG

import os.path as op
_BASEDIR =  op.normpath(op.join(op.realpath(__file__), '../../../..')) + '/'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
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
LANGUAGE_CODE = 'en'

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

# Available interface translations. Listed alphabetically (by you) by language self name. Non-latin charset names listed as if transliterated to latin script. Has to be activated in your local django global_settings.py as well to take effect.
LANGUAGES = (
  ('ar', 'العربية'),	# Transliterated to "al'erebyh" by http://mylanguages.org/arabic_romanization.php
  ('ast', 'Asturianu'),
  ('br', 'Brezhoneg'),
  ('bxr', 'Буряад'),  # Transliterated to "Buryaad"
  ('cs', 'Česky'),  
  ('da', 'Dansk'),
  ('de', 'Deutsch'),
  ('en', 'English'),
  ('es', 'Español'),
  ('fr', 'Français'),
  ('ia', 'Interlingua'),
  ('is', 'Íslenska'),
  ('it', 'Italiano'),
  ('hu', 'Magyar'),
  ('mk', 'Македонски'),  # Transliterated to "Makedonski" by http://translit.cc/
  ('nl', 'Nederlands'),  
  ('nb', 'Norsk (bokmål)'),
  ('nn', 'Norsk (nynorsk)'),
  ('pt', 'Português'),
  ('ru', 'Русский'),    # Transliterated to "Russkij" by http://translit.cc/
  ('fi', 'Suomi'),
  ('sv', 'Svenska'),
  ('vi', 'Tiếng Việt'),
  ('tr', 'Türkçe'),
  #('zh-cn', '中文(简体)'), # Transliterated to "Zhōngwén"
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

LOCALEURL_USE_ACCEPT_LANGUAGE = True
PREFIX_DEFAULT_LOCALE = True
LOCALE_REDIRECT_PERMANENT = False

LOCALE_PATHS = ( _BASEDIR + 'locale', )

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'localeurl.middleware.LocaleURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

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
     'markupfilter',
#    'django.contrib.auth',
#    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#    'django.contrib.sites',
#    'django.contrib.gis',
)

ROUTEMAP_NOMINATIM_URL = 'http://nominatim.openstreetmap.org/search'
