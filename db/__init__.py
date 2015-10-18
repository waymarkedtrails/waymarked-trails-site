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

# add config path
import os, sys
basepath = os.path.normpath(os.path.join(os.path.realpath(__file__), '../../config'))
sys.path.append(basepath)

"""Load configuration settings from a map-specific module.

   The module must be supplied in the environment variable
   ROUTEMAPDB_CONF_MODULE. All upper case variables from the
   module will then be imported into this module.

   (Idea borrowed from Django's configuration module.)
"""

class _ConfigurationHandler:
    """ Class that reads a custom configuration and exports it as attributes.
    """
    def __init__(self):
        self.loaded = False

    def load_config(self):
        import sys
        import os

        self.loaded = True

        if 'ROUTEMAPDB_CONF_MODULE' in os.environ:
            modname = os.environ['ROUTEMAPDB_CONF_MODULE']
            __import__(modname)

            for var in dir(sys.modules[modname]):
                if var.isupper():
                    setattr(self, var, getattr(sys.modules[modname], var))
        else:
            print('WARNING: ROUTEMAPDB_CONF_MODULE not set, using default configuration')


    def isdef(self, attr):
        if not self.loaded:
            self.load_config()
        return hasattr(self, attr)

    def get(self, attr, default=None):
        if not self.loaded:
            self.load_config()
        if hasattr(self, attr):
            return getattr(self, attr)
        elif callable(default):
            return default()
        else:
            return default

conf = _ConfigurationHandler()

