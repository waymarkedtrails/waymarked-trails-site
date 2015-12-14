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

SITECONF_DIR = op.join(PROJECT_DIR, 'config/tiles')
LOCALE_DIR = op.join(PROJECT_DIR, 'django/locale')
MEDIA_ROOT = op.join(PROJECT_DIR, 'frontend/static')

MEDIA_URL = '/static'
API_URL = '/api'
BASE_URL = 'http://localhost:8080'

#############################################################################
#
# Database settings

DB_NAME = 'planet'
DB_USER = None
DB_PASSWORD = None

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

