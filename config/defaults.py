# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2015 Sarah Hoffmann
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

#############################################################################
#
# Path settings

import os.path as op
PROJECT_DIR =  op.normpath(op.join(op.realpath(__file__), '../..'))

LOCALE_DIR = op.join(PROJECT_DIR, 'django/locale')
MEDIA_ROOT = op.join(PROJECT_DIR, 'frontend/static')
OSMC_EXAMPLE_PATH = op.join(PROJECT_DIR, 'frontend/static/img/osmc')

MEDIA_URL = '/static'
API_URL = '/api'
BASE_URL = ''
HILLSHADING_URL = '/hillshading'
GUIDEPOST_URL = 'https://osm.mueschelsoft.de/destinationsign/'

REPLICATION_URL='http://planet.openstreetmap.org/replication/minute/'
REPLICATION_SIZE=50

BASEMAPS = (
  { 'id' : "osm-mapnik",
    'name' : "OSM Standard Map",
    'url' : "https://{a-c}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    'attribution' : ""
  },
)


#############################################################################
#
# Locales

LANGUAGES = (
  ('ar', 'العربية'),    # Transliterates to "al'erebyh" at http://mylanguages.org/arabic_romanization.php
  ('ast', 'Asturianu'),
  ('az', 'Azərbaycanca'),
  ('id', 'Bahasa Indonesia'),
  ('ms', 'Bahasa Melayu'),
  ('be-tarask', 'беларуская'), # transliterates to Belarusian (Taraškievica orthography)
  ('br', 'Brezhoneg'),
  ('bg', 'Български'),  
  ('bxr', 'Буряад'),  # Transliterates to "Buryaad"
  ('ca', 'Català'),
  ('cs', 'Česky'),  
  ('da', 'Dansk'),
  ('de', 'Deutsch'),
  ('et', 'Eesti'),
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
  ('lt', 'Lietuvių'),
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
  ('ro', 'Română'),
  ('ru', 'Русский'),    # Transliterates to "Russkij" (http://translit.cc/)
  ('fi', 'Suomi'),
  ('sk', 'Slovenčina'),
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
  ('zh-hant', '中文(繁體)'), # Transliterates to "Traditional Chinese"
  ('no', ''), # Unspecified Norwegian. Points to "nb".
)


#############################################################################
#
# Database settings

DB_NAME = 'planet'
DB_USER = None
DB_PASSWORD = None
DB_RO_USER = 'www-data'
DB_NODESTORE = None

#############################################################################
#
# Elevation profiles

DEM_FILE = op.join(PROJECT_DIR, 'dem/900913/earth.vrt')
DEM_ACCURACY = 15
DEM_ROUNDING = 5


#############################################################################
#
# Local settings

try:
    from config.local import *
except ImportError:
    pass # no local settings provided

