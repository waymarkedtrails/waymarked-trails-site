# This file is part of Waymarked Trails Map Project
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

# Django settings for tileserv project.

from siteconfig import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECTDIR + 'tiles.sqlite',
        'USER' : 'osm',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

USE_I18N = False
USE_L10N = False


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'tileserv.urls'

INSTALLED_APPS = (
    'django.contrib.contenttypes',
)

TILE_TABLES = {
    'skating' : { 'style' : PROJECTDIR + 'db/styles/skatingmap.xml' },
    'mtb' : { 'style' : PROJECTDIR + 'db/styles/mtbmap.xml' },
    'hiking' : { 'style' : PROJECTDIR + 'db/styles/hikingmap.xml' },
    'cycling' : { 'style' : PROJECTDIR + 'db/styles/cyclingmap.xml' },
}
EMPTY_TILE = PROJECTDIR + 'static/img/empty.png'
TILE_MAXZOOM = 18
