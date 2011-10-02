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
from conf import settings as conf
import PythonMagick as pm
import PythonMagick._PythonMagick as pmi

def make_symbol(tags, region, level, symboltypes):
    """Create a new symbol object from the given set of tags
       from a list of types.
    """
    for c in symboltypes:
        if c.is_class(tags, region):
            return c(tags, region, level)

    return None


class SymbolReference(object):
    """A simple symbol only displaying a reference.

       If a ref tag is found, it will be used for the shield name. Otherwise,
       a pseudo reference is derived from the name by first trying all
       major letters and if that doesn't help the first part of the name.

       Font, size and color of the text can be configured in :mod:`conf`.
    """

    @staticmethod
    def is_class(tags, region):
        return 'ref' in tags or 'osmc:symbol' in tags or 'name'in tags or 'osmc:name' in tags

    def __init__(self, tags, region, level):
        self.level = level/10
        self.ref = ''

        if 'ref' in tags:
            self.ref = re.sub(' ', '', tags['ref'])[:5].upper()
        elif 'osmc:symbol' in tags:
            parts = tags['osmc:symbol'].split(':')
            if len(parts) > 3:
                self.ref = parts[3][:5].upper()

        if not self.ref:
            # try some magic with the name
            if 'name' in tags:
                self.ref = re.sub('[^A-Z]+', '',tags['name'])[:3]
                if not self.ref:
                    self.ref = re.sub(' ', '', tags['name'])[:3].upper()
            elif 'osmc:name' in tags:
                self.ref = re.sub('[^A-Z]+', '',tags['osmc:name'])[:3]
                if not self.ref:
                    self.ref = tags['osmc:name'][:3].upper()
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



class SwissMobileReference(object):
    """Symboles for Swiss Mobile networks
    """

    operator_names = ('swiss mobility',
                      'wanderland schweiz', 
                      'schweiz mobil'
                     )

    @staticmethod
    def is_class(tags, region):
        return tags.get('operator', '').lower() in SwissMobileReference.operator_names and \
                   tags.get('network', '') in ('nwn', 'rwn') and 'ref' in tags

    def __init__(self, tags, region, level):
        self.ref = tags['ref'].strip()[:5]
        self.level = min(len(self.ref),2)

    def get_id(self):
        return 'swiss_%s' % self.ref

    def write_image(self, filename):
        width = 8 + len(self.ref)*7
        img = pm.Image("%dx%d" % (width, conf.SYMBOLS_IMAGE_SIZE[1]),
                       conf.SYMBOLS_SWISS_BGCOLOR)
        img.borderColor(conf.SYMBOLS_BGCOLORS[self.level])
        img.border("1x1")
        img.fillColor(conf.SYMBOLS_TEXT_COLOR)
        img.font('DejaVu-Sans-Bold')
        img.transformSkewX(-20)
        img.fontPointsize(12)
        img.annotate(self.ref.encode('utf-8'), pmi.GravityType.SouthGravity)
        img.write(filename.encode('utf-8'))
        

class KCTReference(object):
    """Symbols used in the Czech Republic and in Slovakia.
    """

    @staticmethod
    def is_class(tags, region):
        # slovakian system
        if (tags.get('operator', '').lower() == 'kst' and 
                tags.get('colour') in conf.SYMBOLS_KCTCOLORS and 
                tags.get('symbol') in conf.SYMBOLS_KCTTYPES):
            return True
        # Czech system
        for k in tags:
            if k.startswith('kct_'):
                return k[4:] in conf.SYMBOLS_KCTCOLORS and tags[k] in conf.SYMBOLS_KCTTYPES

    def __init__(self, tags, region, level):
        self.level = level/10
        if tags.get('operator', '').lower() == 'kst': 
            # Slovakian system
            self.symbol = "%s-%s"% (tags['colour'], tags['symbol'])
        else:
            # Czech system
            for k in tags:
                if k.startswith('kct_'):
                    self.symbol = '%s-%s' % (k[4:], tags[k])
                    break



    def get_id(self):
        return 'kct_%d_%s' % (self.level, self.symbol)

    def write_image(self, filename):
        img = pm.Image(os.path.join(conf.SYMBOLS_KCTSYMPATH, 
                       "%s.png" % self.symbol).encode('utf-8')) 
        img.borderColor(conf.SYMBOLS_BGCOLORS[self.level])
        img.border("1x1")
        img.write(filename.encode('utf-8'))
        


class OSMCSymbolReference(object):
    """Shield described with osmc:symbol description.

       This is a reduced version only. Only one foreground
       symbol is supported and the foreground symbol is mandatory.

       No letters on colorful background anymore. Sorry.
    """

    @staticmethod
    def is_class(tags, region):
        if 'osmc:symbol' in tags:
            parts = parts = tags['osmc:symbol'].split(':', 4)
            return len(parts) > 2 and (parts[2].strip() in OSMCSymbolReference.symbols)

        return False

    def __init__(self, tags, region, level):
        self.level = level/10
        self.ref = ''
        parts = parts = tags['osmc:symbol'].split(':', 4)
        if len(parts) > 1:
            self.bgcolor = parts[1].strip()
            if not self.bgcolor in OSMCSymbolReference.bgsymbols:
                self.bgcolor = 'empty'
            if len(parts) > 2:
                self.symbol = parts[2].strip()
                if len(parts) > 3:
                    self.ref = parts[3].strip()
                    # XXX hack warning, limited support of 
                    # second foreground on request of Isreali
                    # mappers
                    if self.symbol == 'blue_stripe' and self.ref in (
                           'orange_stripe_right', 'green_stripe_right'):
                        self.symbol = 'blue_stripe'+ref[:ref.index('_')]
                        self.ref = ''
                    else:
                        if len(self.ref)>3:
                            self.ref = ''
                        else:
                            self.textcolor = 'black'
                            if len(parts) > 4:
                                self.textcolor = parts[4].strip().encode('utf-8')
                                if self.textcolor not in conf.SYMBOLS_SM_TEXT_COLORS:
                                    self.textcolor = 'black'


    def get_id(self):
        if self.ref:
            return 'osmc_%d_%s_%s_%s_%s' % (self.level, self.bgcolor, self.symbol,
                                         ''.join(["%04x" % ord(x) for x in self.ref]),
                                         self.textcolor)
        else:
            return "osmc_%d_%s_%s" % (self.level, self.bgcolor, self.symbol)

    def write_image(self, filename):
        img = pm.Image(os.path.join(conf.SYMBOLS_OSMCSYMBOLPATH, 
                                    "%s.png" % self.symbol).encode('utf-8'))
        if self.bgcolor is not None:
            imgbg = pm.Image(os.path.join(conf.SYMBOLS_OSMCBGSYMBOLPATH, 
                                          "%s.png" % self.bgcolor).encode('utf-8'))
            img.composite(imgbg, pmi.GravityType.CenterGravity, 
                          pmi.CompositeOperator.DstOverCompositeOp)
        img.compose(pmi.CompositeOperator.CopyCompositeOp)
        img.borderColor(conf.SYMBOLS_BGCOLORS[self.level])
        img.border("1x1")
        if self.ref:
            img.fillColor(self.textcolor)
            img.font('DejaVu-Sans-Condensed-Bold')
            img.fontPointsize(12 if len(self.ref)==1 else 8)
            img.annotate(self.ref.encode('utf-8'), pmi.GravityType.CenterGravity)
        img.write(filename.encode('utf-8'))



    def _get_symbols(path):
        sms = []
        try:
            files = os.listdir(path)
        except:
            print "Warning: cannot read directory for symbols:", path
            return None

        for fn in files:
            m = re.match('(.*).png', fn)
            if m is not None:
                sms.append(m.group(1))
        return sms

    # find all valid symbols
    bgsymbols = _get_symbols(conf.SYMBOLS_OSMCBGSYMBOLPATH)
    symbols = _get_symbols(conf.SYMBOLS_OSMCSYMBOLPATH)



class Dummy(object):
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

