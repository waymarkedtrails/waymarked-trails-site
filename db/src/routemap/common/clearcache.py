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



# Hack to import settings from Django
import os, sys
basepath = os.path.normpath(os.path.join(os.path.realpath(__file__), '../../../../../'))
sys.path.append(os.path.join(basepath, 'django/src/routemap/'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'common.settings'
from django.core.cache import cache


# Clear elevation cache. Cache settings can be found in 
# applications settings file. 
def clearElevationProfileCache(relationid):
    cache.delete(relationid)