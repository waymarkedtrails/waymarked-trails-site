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

import sys
import os

"""Load configuration settings from a map-specific module.

   The module must be supplied in the environment variable
   ROUTEMAPDB_CONF_MODULE. All upper case variables from the
   module will then be imported into this module.

   (Idea borrowed from Django's configuration module.)
"""

modname = os.environ['ROUTEMAPDB_CONF_MODULE']
__import__(modname)

for var in dir(sys.modules[modname]):
    if var.isupper():
        globals()[var] = getattr(sys.modules[modname], var)
