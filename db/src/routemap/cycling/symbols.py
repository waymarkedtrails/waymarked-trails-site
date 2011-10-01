# This file is part of Lonvia's Hiking Map
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
"""Hiking shield generator.

   There are different classes of shield, each having its own class to handle
   creation of the symbols. In order to implement a new shield class three
   functions have to be supplied:

   * 'is_class()' is a static function that receives a map of OSM tags
     and a region id and decides whether the class is applicable.
   * 'get_id()' returns a unique string that can be used to identify
     the shield class and content. It must be a valid filename.
   * 'write_image()' writes the symbol to the given file.

   All configuration concerning the look of the symbols should go into
   :class:`conf.Symbols`.
"""

import os
import re
import conf
import PythonMagick as pm
import PythonMagick._PythonMagick as pmi

class CyclingSymbolDescriptor(object):
    """Description of the hiking symbol (or way shield).
    """

    def __init__(self, tags):
        raise Exception("Abstract class. Use make_symbol() to create objects.")

    @staticmethod
    def make_symbol(tags, region, level):
        """Create a new symbol object from the given
           set of tags.
        """
        # The different symbol types. Order actually matters.
        symboltypes = (
            SymbolReference,
        )
        for c in symboltypes:
            if c.is_class(tags, region):
                return c(tags, region, level)

        return None


class SymbolReference(CyclingSymbolDescriptor):
    """A simple symbol only displaying a reference.

       If a ref tag is found, it will be used for the shield name. Otherwise,
       a pseudo reference is derived from the name by first trying all
       major letters and if that doesn't help the first part of the name.

       Font, size and color of the text can be configured in :mod:`conf`.
    """

    @staticmethod
    def is_class(tags, region):
        return 'ref' in tags or 'name'in tags 

    def __init__(self, tags, region, level):
        self.level = level/10
        self.ref = ''

        if 'ref' in tags:
            self.ref = re.sub(' ', '', tags['ref'])[:5].upper()
        # try some magic with the name
        elif 'name' in tags:
            self.ref = re.sub('[^A-Z]+', '',tags['name'])[:3]
            if not self.ref:
                self.ref = re.sub(' ', '', tags['name'])[:3].upper()
        # must give up at this point

    def get_id(self):
        # dump ref in hex to make sure it is a valid filename
        return "ref_%d_%s" % (self.level, ''.join(["%04x" % ord(x) for x in self.ref]))

    def write_image(self, filename):
        if len(self.ref) <= 3:
            width = len(self.ref)*8+conf.SYMBOLS_IMAGE_SIZE[0]
        else:
            width = len(self.ref)*6+conf.SYMBOLS_IMAGE_SIZE[0]
        img = pm.Image("%dx%d" % (width, conf.SYMBOLS_IMAGE_SIZE[1]-6),
                       conf.SYMBOLS_TEXT_BGCOLOR)
        img.borderColor(conf.SYMBOLS_BGCOLORS[self.level])
        img.border("3x3")
        img.fillColor(conf.SYMBOLS_TEXT_COLOR)
        img.font('DejaVu-Sans-Condensed-Bold')
        img.fontPointsize(9 if len(self.ref)<=3 else 8)
        img.annotate(self.ref.encode('utf-8'), pmi.GravityType.CenterGravity)
        img.write(filename.encode('utf-8'))




class Dummy(CyclingSymbolDescriptor):
    """ Just for Copy'n'Paste when creating new symbol classes.
    """

    @staticmethod
    def is_class(tags, region):
        return False

    def __init__(self, tags, region, level):
        pass

    def get_id(self):
        pass

    def write_image(self, filename):
        pass

