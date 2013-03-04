# -*- coding: utf-8
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
import cairo
import pango
import pangocairo
from math import pi

def make_symbol(tags, region, level, symboltypes):
    """Create a new symbol object from the given set of tags
       from a list of types.
    """
    for c in symboltypes:
        if c.is_class(tags, region):
            return c(tags, region, level)

    return None


def get_symbol(level, cntry, tags, symboltypes):
    """Determine the symbol to use for the way and make sure
       that there is a bitmap in the filesystem.
    """

    sym = make_symbol(tags, cntry, level, symboltypes)

    if sym is None:
        return None

    symid = sym.get_id()

    symfn = os.path.join(conf.WEB_SYMBOLDIR, "%s.png" % symid)

    if not os.path.isfile(symfn):
        sym.write_image(symfn)

    return symid


class ColorBoxReference(object):
    """ Creates an unmarked colored box according to the color tag.
    """

    @staticmethod
    def is_class(tags, region):
        color = tags.get_firstof(('color', 'colour'))
        if color is None or not re.match('#[0-9A-Fa-f]{6}$', color):
            return False

        for k,v in conf.SYMBOLS_COLORBOX_TAGS.iteritems():
            if tags.get(k) == v:
                return True

        return False

    def __init__(self, tags, region, level):
        self.level = level/10
        color = tags.get_firstof(('color', 'colour'))
        m = re.match('#(..)(..)(..)', color)
        self.color = ((1.0+int(m.group(1),16))/256.0,
                      (1.0+int(m.group(2),16))/256.0,
                      (1.0+int(m.group(3),16))/256.0)
        self.colorname = color[1:]


    def get_id(self):
        return "cbox_%d_%s" % (self.level, self.colorname)

    def write_image(self, filename):
        w, h = conf.SYMBOLS_IMAGE_SIZE

        # create an image where the text fits
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(img)

        ctx.scale(w,h)

        # background fill
        ctx.set_source_rgb(*self.color)
        ctx.rectangle(0, 0, 1, 1)
        ctx.fill()

        # border
        ctx.scale(1.0/w,1.0/h)
        ctx.rectangle(0, 0, w, h)
        ctx.set_line_width(conf.SYMBOLS_IMAGE_BORDERWIDTH)
        levcol = conf.SYMBOLS_LEVELCOLORS[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        img.write_to_png(filename)


class SymbolReference(object):
    """A simple symbol only displaying a reference.

       If a ref tag is found, it will be used for the shield name. Otherwise,
       a pseudo reference is derived from the name by first trying all
       major letters and if that doesn't help the first part of the name.

       Font, size and color of the text can be configured in :mod:`conf`.
    """
    # need this to figure out the size of the label
    txtctx_layout = pangocairo.CairoContext(cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 10,10))).create_layout()
    txtfont = pango.FontDescription(conf.SYMBOLS_TEXT_FONT)
    txtctx_layout.set_font_description(txtfont)


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
        # get text size
        self.txtctx_layout.set_text(self.ref)
        tw, th = self.txtctx_layout.get_pixel_size()

        # create an image where the text fits
        w = int(conf.SYMBOLS_TEXT_BORDERWIDTH+2*conf.SYMBOLS_IMAGE_BORDERWIDTH+tw)
        h = conf.SYMBOLS_IMAGE_SIZE[1]
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(img)

        # background fill
        ctx.rectangle(0, 0, w, h)
        ctx.set_source_rgb(*conf.SYMBOLS_TEXT_BGCOLOR)
        ctx.fill_preserve()
        # border
        ctx.set_line_width(conf.SYMBOLS_TEXT_BORDERWIDTH)
        levcol = conf.SYMBOLS_LEVELCOLORS[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()
        # reference text
        ctx.set_source_rgb(*conf.SYMBOLS_TEXT_COLOR)
        pctx = pangocairo.CairoContext(ctx)
        pctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        layout = pctx.create_layout()
        layout.set_font_description(self.txtfont)
        layout.set_text(self.ref)
        pctx.update_layout(layout)
        ctx.move_to((w-tw)/2, (h-layout.get_iter().get_baseline()/pango.SCALE)/2.0)
        pctx.show_layout(layout)

        img.write_to_png(filename)



class SwissMobileReference(object):
    """Symboles for Swiss Mobile networks
    """

    @staticmethod
    def is_class(tags, region):
        return tags.get('operator', '').lower() in conf.SYMBOLS_SWISS_OPERATORS and \
                   tags.get('network', '') in conf.SYMBOLS_SWISS_NETWORK and 'ref' in tags

    def __init__(self, tags, region, level):
        self.txtfont = pango.FontDescription(conf.SYMBOLS_SWISS_FONT)
        self.ref = tags['ref'].strip()[:5]
        self.level = min(len(self.ref),2)

    def get_id(self):
        return 'swiss_%s' % self.ref

    def write_image(self, filename):
        w = 8 + len(self.ref)*7
        h = conf.SYMBOLS_IMAGE_SIZE[1]

        # create an image where the text fits
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(img)

        # background fill
        ctx.rectangle(0, 0, w, h)
        ctx.set_source_rgb(*conf.SYMBOLS_SWISS_BGCOLOR)
        ctx.fill_preserve()
        # border
        ctx.set_line_width(conf.SYMBOLS_IMAGE_BORDERWIDTH)
        levcol = conf.SYMBOLS_LEVELCOLORS[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        # text
        ctx.set_source_rgb(*conf.SYMBOLS_TEXT_COLOR)
        pctx = pangocairo.CairoContext(ctx)
        pctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        layout = pctx.create_layout()
        layout.set_font_description(self.txtfont)
        layout.set_text(self.ref)
        tw, th = layout.get_pixel_size()
        pctx.update_layout(layout)
        ctx.move_to(w-tw-conf.SYMBOLS_IMAGE_BORDERWIDTH/2,
                    h-layout.get_iter().get_baseline()/pango.SCALE-conf.SYMBOLS_IMAGE_BORDERWIDTH/2)
        pctx.show_layout(layout)

        img.write_to_png(filename)

class JelReference(object):
    """Hiking symbols used in Hungary. (tag jel)
    """

    @staticmethod
    def is_class(tags, region):
        return 'jel'in tags and tags['jel'] in conf.SYMBOLS_JELTYPES

    def __init__(self, tags, region, level):
        self.level = level/10
        self.symbol = tags['jel']

    def get_id(self):
        return 'jel_%d_%s' % (self.level, self.symbol)

    def write_image(self, filename):
        img = cairo.ImageSurface.create_from_png(
                os.path.join(conf.SYMBOLS_JELSYMPATH,
                             "%s.png" % self.symbol))
        ctx = cairo.Context(img)

        # border
        ctx.rectangle(0, 0,
                      conf.SYMBOLS_IMAGE_SIZE[0],
                      conf.SYMBOLS_IMAGE_SIZE[1])
        ctx.set_line_width(conf.SYMBOLS_IMAGE_BORDERWIDTH)
        levcol = conf.SYMBOLS_LEVELCOLORS[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        img.write_to_png(filename)


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
        img = cairo.ImageSurface.create_from_png(
                os.path.join(conf.SYMBOLS_KCTSYMPATH,
                             "%s.png" % self.symbol))
        ctx = cairo.Context(img)

        # border
        ctx.rectangle(0, 0,
                      conf.SYMBOLS_IMAGE_SIZE[0],
                      conf.SYMBOLS_IMAGE_SIZE[1])
        ctx.set_line_width(conf.SYMBOLS_IMAGE_BORDERWIDTH)
        levcol = conf.SYMBOLS_LEVELCOLORS[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        img.write_to_png(filename)



class OSMCSymbolReference(object):
    """Shield described with osmc:symbol description.

       This is a reduced version only. Only one foreground
       symbol is supported and the foreground symbol is mandatory.

       No letters on colorful background anymore. Sorry.
    """

    txtfont = pango.FontDescription(conf.SYMBOLS_TEXT_FONT)

    @staticmethod
    def is_class(tags, region):
        if 'osmc:symbol' in tags:
            parts = parts = tags['osmc:symbol'].split(':', 4)
            if len(parts) > 2:
                fg = parts[2].strip()
                if fg == 'shell_modern':
                    return True
                idx = fg.find('_')
                if idx > 0:
                    if not fg[:idx] in conf.SYMBOLS_OSMC_COLORS:
                        return False
                    fg = fg[idx+1:]
                return hasattr(OSMCSymbolReference, 'paint_fg_' + fg)

        return False

    def __init__(self, tags, region, level):
        self.level = level/10
        self.ref = ''
        parts = parts = tags['osmc:symbol'].split(':', 4)
        if len(parts) > 1:
            self._set_bg_symbol(parts[1].strip())
            if len(parts) > 2:
                self._set_fg_symbol(parts[2].strip())
                if len(parts) > 3:
                    self.ref = parts[3].strip()
                    # XXX hack warning, limited support of
                    # second foreground on request of Isreali
                    # mappers
                    if self.fgsymbol == 'blue_stripe' and self.ref in (
                           'orange_stripe_right', 'green_stripe_right'):
                        self.fgsecondary = ref[:ref.index('_')]
                        self.ref = ''
                    else:
                        if len(self.ref)>3:
                            self.ref = ''
                        else:
                            self.textcolor = 'black'
                            if len(parts) > 4:
                                self.textcolor = parts[4].strip().encode('utf-8')
                                if self.textcolor not in conf.SYMBOLS_OSMC_COLORS:
                                    self.textcolor = 'black'

    def _set_bg_symbol(self, symbol):
        self.bgsymbol = None
        self.bgcolor = None
        idx = symbol.find('_')
        if idx < 0:
            if symbol in conf.SYMBOLS_OSMC_COLORS:
                self.bgcolor = symbol
        else:
            col = symbol[:idx]
            sym = symbol[idx+1:]
            if col in conf.SYMBOLS_OSMC_COLORS and hasattr(self, 'paint_bg_' + sym):
                self.bgsymbol = sym
                self.bgcolor = col

    def _set_fg_symbol(self, symbol):
        self.fgsecondary = None
        if symbol == 'shell_modern':
            self.fgcolor = None
            self.fgsymbol = 'shell_modern'
        else:
            idx = symbol.find('_')
            if idx < 0:
                self.fgsymbol = symbol
                self.fgcolor = None
            else:
                self.fgcolor = symbol[:idx]
                self.fgsymbol = symbol[idx+1:]


    def get_id(self):
        if self.bgcolor is None:
            bg = 'empty' # for compatibility
        else:
            if self.bgsymbol is None:
                bg = self.bgcolor
            else:
                bg = '%s_%s' % (self.bgcolor, self.bgsymbol)
        if self.fgcolor is None:
            fg = self.fgsymbol
        else:
            fg = '%s_%s' % (self.fgcolor, self.fgsymbol)
        if self.fgsecondary is not None:
            fg = '%s_%s' % (fg, self.fgsecondary)

        if self.ref:
            return 'osmc_%d_%s_%s_%s_%s' % (self.level, bg, fg,
                                         ''.join(["%04x" % ord(x) for x in self.ref]),
                                         self.textcolor)
        else:
            return "osmc_%d_%s_%s" % (self.level, bg, fg)

    def write_image(self, filename):
        w, h = conf.SYMBOLS_IMAGE_SIZE

        # create an image where the text fits
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(img)

        ctx.scale(w,h)

        # background fill
        if self.bgcolor is not None:
            if self.bgsymbol is None:
                ctx.set_source_rgb(*conf.SYMBOLS_OSMC_COLORS[self.bgcolor])
            else:
                if self.bgcolor == 'white':
                    ctx.set_source_rgb(*conf.SYMBOLS_OSMC_COLORS['black'])
                else:
                    ctx.set_source_rgb(*conf.SYMBOLS_OSMC_COLORS['white'])
        else:
            ctx.set_source_rgba(0,0,0,0) # transparent
        ctx.rectangle(0, 0, 1, 1)
        ctx.fill()

        ctx.save()
        if self.bgsymbol is not None:
            ctx.translate(0.2,0.2)
            ctx.scale(0.6,0.6)


        # foreground fill
        ctx.set_source_rgb(*conf.SYMBOLS_OSMC_COLORS[self.fgcolor if self.fgcolor is not None else 'black'])
        ctx.set_line_width(0.3)
        func = getattr(self, 'paint_fg_' + self.fgsymbol)
        func(ctx)

        ctx.restore()
        if self.bgsymbol is not None:
            ctx.set_source_rgb(*conf.SYMBOLS_OSMC_COLORS[self.bgcolor])
            func = getattr(self, 'paint_bg_' + self.bgsymbol)
            func(ctx)

        # border
        ctx.scale(1.0/w,1.0/h)
        ctx.rectangle(0, 0, w, h)
        ctx.set_line_width(conf.SYMBOLS_IMAGE_BORDERWIDTH)
        levcol = conf.SYMBOLS_LEVELCOLORS[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()


        # text
        if self.ref:
            ctx.set_source_rgb(*conf.SYMBOLS_OSMC_COLORS[self.textcolor])
            pctx = pangocairo.CairoContext(ctx)
            pctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
            layout = pctx.create_layout()
            layout.set_font_description(self.txtfont)
            layout.set_text(self.ref)
            tw, th = layout.get_pixel_size()
            sc = 1.0
            if tw > w:
                sc = (float(w) - conf.SYMBOLS_IMAGE_BORDERWIDTH)/tw
                ctx.scale(sc, sc)
            pctx.update_layout(layout)
            ctx.move_to((w-sc*tw)/2, (h-sc*layout.get_iter().get_baseline()/pango.SCALE)/2.0)
            pctx.show_layout(layout)

        img.write_to_png(filename)

    def paint_bg_circle(self, ctx):
        ctx.set_line_width(0.1)
        ctx.arc(0.5, 0.5, 0.4, 0, 2*pi)
        ctx.stroke()

    def paint_bg_frame(self, ctx):
        ctx.set_line_width(0.1)
        ctx.rectangle(0.15, 0.15, 0.7, 0.7)
        ctx.stroke()

    def paint_fg_arch(self, ctx):
        ctx.set_line_width(0.22)
        ctx.move_to(0.25,0.9)
        ctx.arc(0.5,0.5,0.25, pi, 0)
        ctx.line_to(0.75,0.9)
        ctx.stroke()

    def paint_fg_backslash(self, ctx):
        ctx.move_to(0, 0)
        ctx.line_to(1, 1)
        ctx.stroke()

    def paint_fg_bar(self, ctx):
        ctx.move_to(0, 0.5)
        ctx.line_to(1, 0.5)
        ctx.stroke()

    def paint_fg_circle(self, ctx):
        ctx.set_line_width(0.21)
        ctx.arc(0.5, 0.5, 0.33, 0, 2*pi)
        ctx.stroke()

    def paint_fg_cross(self, ctx):
        ctx.move_to(0, 0.5)
        ctx.line_to(1, 0.5)
        ctx.stroke()
        ctx.move_to(0.5, 0)
        ctx.line_to(0.5, 1)
        ctx.stroke()

    def paint_fg_diamond_line(self, ctx):
        ctx.set_line_width(0.15)
        ctx.move_to(0.1, 0.5)
        ctx.line_to(0.5, 0.1)
        ctx.line_to(0.9, 0.5)
        ctx.line_to(0.5, 0.9)
        ctx.close_path()
        ctx.stroke()

    def paint_fg_diamond(self, ctx):
        ctx.move_to(0, 0.5)
        ctx.line_to(0.5, 0.25)
        ctx.line_to(1, 0.5)
        ctx.line_to(0.5, 0.75)
        ctx.fill()

    def paint_fg_dot(self, ctx):
        ctx.arc(0.5, 0.5, 0.37, 0, 2*pi)
        ctx.fill()

    def paint_fg_fork(self, ctx):
        ctx.set_line_width(0.15)
        ctx.move_to(1, 0.5)
        ctx.line_to(0.45, 0.5)
        ctx.line_to(0, 0.1)
        ctx.stroke()
        ctx.move_to(0.45, 0.5)
        ctx.line_to(0, 0.9)
        ctx.stroke()

    def paint_fg_lower(self, ctx):
        ctx.rectangle(0, 0.5, 1, 1)
        ctx.fill()

    def paint_fg_pointer(self, ctx):
        ctx.move_to(0.1, 0.1)
        ctx.line_to(0.1, 0.9)
        ctx.line_to(0.9, 0.5)
        ctx.fill()

    def paint_fg_rectangle_line(self, ctx):
        ctx.set_line_width(0.15)
        ctx.rectangle(0.25, 0.25, 0.5, 0.5)
        ctx.stroke()

    def paint_fg_rectangle(self, ctx):
        ctx.rectangle(0.25, 0.25, 0.5, 0.5)
        ctx.fill()

    def paint_fg_red_diamond(self, ctx):
        ctx.move_to(0, 0.5)
        ctx.line_to(0.5, 0.25)
        ctx.line_to(0.5, 0.75)
        ctx.fill()
        ctx.set_source_rgb(*conf.SYMBOLS_OSMC_COLORS['red'])
        ctx.move_to(0.5, 0.25)
        ctx.line_to(1, 0.5)
        ctx.line_to(0.5, 0.75)
        ctx.fill()

    def paint_fg_slash(self, ctx):
        ctx.move_to(1, 0)
        ctx.line_to(0, 1)
        ctx.stroke()

    def paint_fg_stripe(self, ctx):
        ctx.move_to(0.5, 0)
        ctx.line_to(0.5, 1)
        ctx.stroke()

    def paint_fg_triangle_line(self, ctx):
        ctx.set_line_width(0.15)
        ctx.move_to(0.2, 0.8)
        ctx.line_to(0.5, 0.2)
        ctx.line_to(0.8, 0.8)
        ctx.close_path()
        ctx.stroke()

    def paint_fg_triangle(self, ctx):
        ctx.move_to(0.2, 0.8)
        ctx.line_to(0.5, 0.2)
        ctx.line_to(0.8, 0.8)
        ctx.fill()

    def paint_fg_triangle_turned(self, ctx):
        ctx.move_to(0.2, 0.2)
        ctx.line_to(0.5, 0.8)
        ctx.line_to(0.8, 0.2)
        ctx.fill()

    def paint_fg_turned_T(self, ctx):
        ctx.set_line_width(0.2)
        ctx.move_to(0.1, 0.8)
        ctx.line_to(0.9, 0.8)
        ctx.move_to(0.5, 0.2)
        ctx.line_to(0.5, 0.8)
        ctx.stroke()

    def paint_fg_x(self, ctx):
        ctx.set_line_width(0.25)
        ctx.move_to(1, 0)
        ctx.line_to(0, 1)
        ctx.move_to(0, 0)
        ctx.line_to(1, 1)
        ctx.stroke()

    def paint_fg_shell(self, ctx):
        al = ctx.get_antialias()
        #ctx.set_antialias(cairo.ANTIALIAS_NONE)
        if self.fgcolor is None:
            ctx.set_source_rgb(*conf.SYMBOLS_OSMC_COLORS['black'])
        ctx.set_line_width(0.06)
        ctx.move_to(0.5,0.1)
        ctx.line_to(0,0.3)
        ctx.move_to(0.5,0.1)
        ctx.line_to(0.1,0.5)
        ctx.move_to(0.5,0.1)
        ctx.line_to(0.2,0.65)
        ctx.move_to(0.5,0.1)
        ctx.line_to(0.35,0.8)
        ctx.move_to(0.5,0.1)
        ctx.line_to(0.5,0.85)
        ctx.move_to(0.5,0.1)
        ctx.line_to(0.65,0.8)
        ctx.move_to(0.5,0.1)
        ctx.line_to(0.8,0.65)
        ctx.move_to(0.5,0.1)
        ctx.line_to(0.9,0.5)
        ctx.move_to(0.5,0.1)
        ctx.line_to(1,0.3)
        ctx.stroke()
        ctx.set_antialias(al)

    def paint_fg_shell_modern(self, ctx):
        al = ctx.get_antialias()
        #ctx.set_antialias(cairo.ANTIALIAS_NONE)
        if self.fgcolor is None:
            ctx.set_source_rgb(*conf.SYMBOLS_OSMC_COLORS['white'])
        ctx.set_line_width(0.06)
        ctx.move_to(0.1,0.5)
        ctx.line_to(0.3,0)
        ctx.move_to(0.1,0.5)
        ctx.line_to(0.5,0.1)
        ctx.move_to(0.1,0.5)
        ctx.line_to(0.65,0.2)
        ctx.move_to(0.1,0.5)
        ctx.line_to(0.8,0.35)
        ctx.move_to(0.1,0.5)
        ctx.line_to(0.85,0.5)
        ctx.move_to(0.1,0.5)
        ctx.line_to(0.8,0.65)
        ctx.move_to(0.1,0.5)
        ctx.line_to(0.65,0.8)
        ctx.move_to(0.1,0.5)
        ctx.line_to(0.5,0.9)
        ctx.move_to(0.1,0.5)
        ctx.line_to(0.3,1)
        ctx.stroke()
        ctx.set_antialias(al)

    def paint_fg_hiker(self, ctx):
        ctx.save()
        src = cairo.ImageSurface.create_from_png(conf.SYMBOLS_OSMCSYMBOLPATH + '/hiker.png')
        ctx.scale(1.0/(src.get_width()+conf.SYMBOLS_IMAGE_BORDERWIDTH),
                  1.0/(src.get_height()+conf.SYMBOLS_IMAGE_BORDERWIDTH))
        ctx.mask_surface(src, conf.SYMBOLS_IMAGE_BORDERWIDTH/2.0, conf.SYMBOLS_IMAGE_BORDERWIDTH/2.0)
        ctx.restore()

    def paint_fg_wheel(self, ctx):
        ctx.save()
        src = cairo.ImageSurface.create_from_png(conf.SYMBOLS_OSMCSYMBOLPATH + '/red_wheel.png')
        ctx.scale(1.0/(src.get_width()+conf.SYMBOLS_IMAGE_BORDERWIDTH),
                  1.0/(src.get_height()+conf.SYMBOLS_IMAGE_BORDERWIDTH))
        ctx.mask_surface(src, conf.SYMBOLS_IMAGE_BORDERWIDTH/2.0, conf.SYMBOLS_IMAGE_BORDERWIDTH/2.0)
        ctx.restore()

class ShieldReference(object):
    """ A prerendered shield.
    """

    @staticmethod
    def is_class(tags, region):
        return (ShieldReference.get_shield_file(tags) is not None)

    def __init__(self, tags, region, level):
        self.shieldfile = self.get_shield_file(tags)
        self.level = level/10

    def get_id(self):
        return 'shield_%d_%s' % (self.level, self.shieldfile)

    def write_image(self, filename):
        img = cairo.ImageSurface.create_from_png(
                os.path.join(conf.SYMBOLS_SHIELDPATH,
                             "%s.png" % self.shieldfile))
        ctx = cairo.Context(img)

        # border
        ctx.rectangle(0, 0, img.get_width(), img.get_height())
        ctx.set_line_width(conf.SYMBOLS_IMAGE_BORDERWIDTH)
        levcol = conf.SYMBOLS_LEVELCOLORS[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        img.write_to_png(filename)

    def load_shieldlist():
        if not hasattr(conf, 'SYMBOLS_SHIELDPATH'):
            return None
        fd = open(os.path.join(conf.SYMBOLS_SHIELDPATH, 'symbols.desc'))
        sl = []
        for ln in fd:
            ln = ln.strip()
            comment = ln.find('#')
            if comment == 0:
                continue
            if comment > 0:
                ln = ln[comment:]
            parts = ln.split(None, 1)
            if len(parts) > 1:
                sl.append((eval(parts[1]), parts[0]))
        fd.close()

        return sl

    shieldlist = load_shieldlist()

    @staticmethod
    def get_shield_file(tags):
        if ShieldReference.shieldlist is None:
            return None
        for (t,f) in ShieldReference.shieldlist:
            for (k,v) in t.iteritems():
                if tags.get(k) != v: break
            else:
                return f


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


if __name__ == "__main__":
    # Testing
    import sys
    import osgende
    if len(sys.argv) != 2:
        print "Usage: python symbol.py <outdir>"
        sys.exit(-1)
    outdir = sys.argv[1]
    symboltypes = (
            SwissMobileReference,
            ColorBoxReference,
            JelReference,
            KCTReference,
            OSMCSymbolReference,
            SymbolReference
        )
    testsymbols = [
        ( 0, '', { 'ref' : '10' }),
        ( 30, '', { 'ref' : '15' }),
        ( 20, '', { 'ref' : 'WWWW' }),
        ( 10, '', { 'ref' : '1' }),
        ( 20, '', { 'ref' : 'Ag' }),
        ( 20, '', { 'ref' : u'１号路' }),
        ( 20, '', { 'ref' : u'يلة' }),
        ( 20, '', { 'ref' : u'하이' }),
        ( 20, '', { 'ref' : u'шие' }),
        ( 10, '', { 'ref' : '7', 'operator' : 'swiss mobility', 'network' : 'nwn'}),
        ( 20, '', { 'ref' : '57', 'operator' : 'swiss mobility', 'network' : 'rwn'}),
        ( 20, '', { 'operator' : 'kst', 'symbol' : 'learning', 'colour' : 'red'}),
        ( 0, '', { 'osmc:symbol' : 'red::blue_lower' }),
        ( 0, '', { 'osmc:symbol' : 'white:white:blue_lower' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_arch' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_backslash' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_bar' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_circle' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_cross' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_diamond_line' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_diamond' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_dot' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_fork' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_pointer' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_rectangle_line' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_rectangle' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_red_diamond' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_slash' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_stripe' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_triangle_line' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_triangle' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_triangle_turned' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_turned_T' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:blue_x' }),
        ( 30, '', { 'osmc:symbol' : 'white:white_circle:yellow_triangle' }),
        ( 30, '', { 'osmc:symbol' : 'white:black_frame:blue_x' }),
        ( 0, '', { 'osmc:symbol' : 'white:blue_frame:red_dot:A' }),
        ( 10, '', { 'osmc:symbol' : 'white:red:white_bar:222' }),
        ( 20, '', { 'osmc:symbol' : 'white:white:shell' }),
        ( 30, '', { 'osmc:symbol' : 'white:black:shell_modern' }),
        ( 30, '', { 'osmc:symbol' : 'white:white:hiker' }),
        ( 30, '', { 'osmc:symbol' : 'white::hiker' }),
        ( 30, '', { 'osmc:symbol' : 'white:brown:white_triangle' }),
        ( 30, '', { 'osmc:symbol' : 'white:gray:purple_fork' }),
        ( 30, '', { 'osmc:symbol' : 'white:green:orange_cross' }),
        ( 30, '', { 'osmc:symbol' : 'white:orange:black_lower' }),
        ( 30, '', { 'osmc:symbol' : 'white:purple:green_turned_T' }),
        ( 30, '', { 'osmc:symbol' : 'white:red:gray_stripe'}),
        ( 30, '', { 'osmc:symbol' : 'white:yellow:brown_diamond_line'}),
        ( 30, '', { 'osmc:symbol' : 'red:white:red_wheel'}),
        ( 30, '', { 'jel' : 'p+', 'ref' : 'xx'}),
        ( 30, '', { 'jel' : 'foo', 'ref' : 'yy'}),
        #( 30, '', { 'operator' : 'Norwich City Council', 'color' : '#FF0000'}),
        #( 30, '', { 'operator' : 'Norwich City Council', 'colour' : '#0000FF'}),
    ]

    for (level, region, tags) in testsymbols:
        sym = make_symbol(osgende.tags.TagStore(tags), region, level, symboltypes)
        symid = sym.get_id()
        symfn = os.path.join(outdir, "%s.png" % symid)

        sym.write_image(symfn)

