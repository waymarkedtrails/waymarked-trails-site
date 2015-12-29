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
""" Shield generation
"""

import re
import os
import cairo
from gi.repository import Pango, PangoCairo, Rsvg
from math import pi

from db.configs import ShieldConfiguration
from db import conf

CONFIG = conf.get('SYMBOLS', ShieldConfiguration)

def _parse_color(color):
    if color in CONFIG.color_names:
        return color, CONFIG.color_names[color]

    m = re.match('#([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})$', color)
    if m:
        return color[1:], ((1.0+int(m.group(1),16))/256.0,
                           (1.0+int(m.group(2),16))/256.0,
                           (1.0+int(m.group(3),16))/256.0)

    return None

def _get_text_size(text):
    # get text size
    txtctx_layout = PangoCairo.create_layout(
                       cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 10,10)))
    txtfont = Pango.FontDescription(CONFIG.text_font)
    txtctx_layout.set_font_description(txtfont)
    txtctx_layout.set_text(text, -1)
    return txtctx_layout.get_pixel_size()


class ColorBox(object):
    """ Creates an unmarked colored box according to the color tag.
    """
    @classmethod
    def create(cls, tags, region, level):
        color = tags.get_firstof(('color', 'colour'))
        if color is not None:
            cinfo = _parse_color(color)
            if cinfo is not None:
                cls(level, cinfo[0], cinfo[1])

        return None

    def __init__(self, level, name, color):
        self.level = int(level/10)
        self.color = color
        self.colorname = name


    def get_id(self):
        return "cbox_%d_%s" % (self.level, self.colorname)

    def write_image(self, filename):
        w, h = CONFIG.image_size

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
        ctx.set_line_width(CONFIG.image_border_width)
        levcol = CONFIG.level_colors[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        img.write_to_png(filename)


class TextSymbol(object):
    """A simple symbol only displaying a reference.

       If a ref tag is found, it will be used for the shield name. Otherwise,
       a pseudo reference is derived from the name by first trying all
       major letters and if that doesn't help the first part of the name.

       Font, size and color of the text can be configured in :mod:`conf`.
    """

    @classmethod
    def create(cls, tags, region, level):
        ref = ''
        if 'ref' in tags:
            ref = re.sub(' ', '', tags['ref'])[:5].upper()
        elif 'osmc:symbol' in tags:
            parts = tags['osmc:symbol'].split(':')
            if len(parts) > 3:
                ref = parts[3][:5].upper()

        if not ref:
            # try some magic with the name
            name = tags.get('name') or tags.get('osmc:name')
            if name is not None:
                ref = re.sub('[^A-Z]+', '', name)[:3]
                if not ref:
                    ref = re.sub(' ', '', name)[:3].upper()

        # must give up at this point
        if not ref:
            return None

        return cls(ref, level)

    def __init__(self, ref, level):
        self.level = int(level/10)
        self.ref = ref


    def get_id(self):
        # dump ref in hex to make sure it is a valid filename
        return "ref_%d_%s" % (self.level, ''.join(["%04x" % ord(x) for x in self.ref]))

    def write_image(self, filename):
        # get text size
        tw, th = _get_text_size(self.ref)

        # create an image where the text fits
        w = int(tw + CONFIG.text_border_width + 2 * CONFIG.image_border_width)
        h = CONFIG.image_size[1]
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(img)

        # background fill
        ctx.rectangle(0, 0, w, h)
        ctx.set_source_rgb(*CONFIG.text_bgcolor)
        ctx.fill_preserve()
        # border
        ctx.set_line_width(CONFIG.text_border_width)
        levcol = CONFIG.level_colors[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()
        # reference text
        ctx.set_source_rgb(*CONFIG.text_color)
        layout = PangoCairo.create_layout(ctx)
        layout.set_font_description(Pango.FontDescription(CONFIG.text_font))
        layout.set_text(self.ref, -1)
        PangoCairo.update_layout(ctx, layout)
        ctx.move_to((w-tw)/2, (h-layout.get_iter().get_baseline()/Pango.SCALE)/2.0)
        PangoCairo.show_layout(ctx, layout)

        img.write_to_png(filename)


class SwissMobile(object):
    """Symboles for Swiss Mobile networks
    """

    @classmethod
    def create(cls, tags, region, level):
        if 'ref' in tags \
           and tags.get('operator', '').lower() in CONFIG.swiss_mobile_operators \
           and tags.get('network', '') in CONFIG.swiss_mobile_networks:
            return cls(tags['ref'])

        return None

    def __init__(self, ref):
        self.ref = ref.strip()[:5]
        self.level = min(len(self.ref),3)

    def get_id(self):
        return 'swiss_%s' % self.ref

    def write_image(self, filename):
        w = 8 + len(self.ref)*7
        h = CONFIG.image_size[1]

        # create an image where the text fits
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(img)

        # background fill
        ctx.rectangle(0, 0, w, h)
        ctx.set_source_rgb(*CONFIG.swiss_mobile_bgcolor)
        ctx.fill_preserve()
        # border
        ctx.set_line_width(CONFIG.image_border_width)
        levcol = CONFIG.level_colors[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        # text
        ctx.set_source_rgb(*CONFIG.swiss_mobile_color)
        layout = PangoCairo.create_layout(ctx)
        layout.set_font_description(Pango.FontDescription(CONFIG.swiss_mobile_font))
        layout.set_text(self.ref, -1)
        tw, th = layout.get_pixel_size()
        PangoCairo.update_layout(ctx, layout)
        ctx.move_to(w - tw - CONFIG.image_border_width/2,
                    h - layout.get_iter().get_baseline()/Pango.SCALE
                      - CONFIG.image_border_width/2)
        PangoCairo.show_layout(ctx, layout)

        img.write_to_png(filename)


class JelRef(object):
    """Hiking symbols used in Hungary. (tag jel)
    """

    @classmethod
    def create(cls, tags, region, level):
        if 'jel'in tags and tags['jel'] in CONFIG.jel_types:
            return cls(tags['jel'], level)

        return None

    def __init__(self, symbol, level):
        self.level = int(level/10)
        self.symbol = symbol

    def get_id(self):
        return 'jel_%d_%s' % (self.level, self.symbol)

    def write_image(self, filename):
        w, h = CONFIG.image_size
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(img)

        rhdl = Rsvg.Handle.new_from_file(
                os.path.join(CONFIG.symbol_dir, CONFIG.jel_path,
                            "%s.svg" % self.symbol))
        dim = rhdl.get_dimensions()
        ctx.save()
        ctx.scale(w/dim.width, h/dim.height)
        rhdl.render_cairo(ctx)
        ctx.restore()

        # border
        ctx.rectangle(0, 0, img.get_width(), img.get_height())
        ctx.set_line_width(CONFIG.image_border_width)
        levcol = CONFIG.level_colors[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        img.write_to_png(filename)


class KCTRef(object):
    """Symbols used in the Czech Republic and in Slovakia.
    """

    @classmethod
    def create(cls, tags, region, level):
        # slovakian system
        if tags.get('operator', '').lower() == 'kst':
            if  tags.get('colour') in CONFIG.kct_colors and \
                tags.get('symbol') in CONFIG.kct_types:
                return cls(tags['colour'], tags['symbol'], level)
        # Czech system
        else:
            for k in tags:
                if k.startswith('kct_'):
                    if k[4:] in CONFIG.kct_colors and tags[k] in CONFIG.kct_types:
                        return cls(k[4:], tags[k], level)

        return None

    def __init__(self, color, symbol, level):
        self.level = int(level/10)
        self.symbol = "%s-%s"% (color, symbol)

    def get_id(self):
        return 'kct_%d_%s' % (self.level, self.symbol)

    def write_image(self, filename):
        img = cairo.ImageSurface.create_from_png(
                os.path.join(CONFIG.symbol_dir, CONFIG.kct_path,
                             "%s.png" % self.symbol))
        ctx = cairo.Context(img)

        # border
        ctx.rectangle(0, 0, img.get_width(), img.get_height())
        ctx.set_line_width(CONFIG.image_border_width)
        levcol = CONFIG.level_colors[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        img.write_to_png(filename)


class OSMCSymbol(object):
    """Shield described with osmc:symbol description.

       This is a reduced version only. Only one foreground
       symbol is supported.
    """


    @classmethod
    def create(cls, tags, region, level):
        if 'osmc:symbol' in tags and ':' in tags['osmc:symbol']:
            return cls(tags['osmc:symbol'], level)

        return None

    def __init__(self, symbol, level):
        self.level = int(level/10)
        self.ref = ''
        parts = symbol.split(':', 4)
        self._set_bg_symbol(parts[1].strip())

        if len(parts) > 2:
            self._set_fg_symbol(parts[2].strip())
        else:
            self.fgsymbol = None
            self.fgcolor = None
            self.fgsecondary = None

        if len(parts) > 3:
            self.ref = parts[3].strip()
            # XXX hack warning, limited support of second foreground on request
            # of Isreali mappers
            if self.fgsymbol == 'blue_stripe' and self.ref in (
                   'orange_stripe_right', 'green_stripe_right'):
                self.fgsecondary = ref[:ref.index('_')]
                self.ref = ''
            else:
                if len(self.ref) > 4:
                    self.ref = ''
                else:
                    self.textcolor = 'black'
                    if len(parts) > 4:
                        self.textcolor = parts[4].strip().encode('utf-8')
                        if self.textcolor not in CONFIG.osmc_colors:
                            self.textcolor = 'black'

    def _set_bg_symbol(self, symbol):
        self.bgsymbol = None
        self.bgcolor = None
        idx = symbol.find('_')
        if idx < 0:
            if symbol in CONFIG.osmc_colors:
                self.bgcolor = symbol
        else:
            col = symbol[:idx]
            sym = symbol[idx+1:]
            if col in CONFIG.osmc_colors and hasattr(self, 'paint_bg_' + sym):
                self.bgsymbol = sym
                self.bgcolor = col

    def _set_fg_symbol(self, symbol):
        self.fgsecondary = None
        if symbol == 'shell_modern':
            self.fgcolor = 'yellow'
            self.fgsymbol = 'shell_modern'
        else:
            idx = symbol.find('_')
            if idx < 0:
                self.fgsymbol = symbol
                self.fgcolor = 'black' if not symbol == 'shell' else 'yellow'
            else:
                self.fgcolor = symbol[:idx] if symbol[:idx] in CONFIG.osmc_colors else 'black'
                self.fgsymbol = symbol[idx+1:]
            if not hasattr(self, 'paint_fg_' + self.fgsymbol):
                self.fgsymbol = None


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
        if len(self.ref) <= 2:
            w, h = CONFIG.image_size
        else:
            w, h = CONFIG.wide_image_size

        # create an image where the text fits
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(img)

        ctx.scale(w, h)

        # background fill
        if self.bgcolor is not None:
            if self.bgsymbol is None:
                ctx.set_source_rgb(*CONFIG.osmc_colors[self.bgcolor])
            else:
                if self.bgcolor == 'white':
                    ctx.set_source_rgb(*CONFIG.osmc_colors['black'])
                else:
                    ctx.set_source_rgb(*CONFIG.osmc_colors['white'])
        else:
            ctx.set_source_rgba(0,0,0,0) # transparent
        ctx.rectangle(0, 0, 1, 1)
        ctx.fill()

        ctx.save()
        if self.bgsymbol is not None:
            ctx.translate(0.2,0.2)
            ctx.scale(0.6,0.6)

        # foreground fill
        if self.fgsymbol is not None:
            ctx.set_source_rgb(*CONFIG.osmc_colors[self.fgcolor])
            ctx.set_line_width(0.3)
            func = getattr(self, 'paint_fg_' + self.fgsymbol)
            func(ctx)

        ctx.restore()
        if self.bgsymbol is not None:
            ctx.set_source_rgb(*CONFIG.osmc_colors[self.bgcolor])
            func = getattr(self, 'paint_bg_' + self.bgsymbol)
            func(ctx)

        # border
        ctx.scale(1.0/w,1.0/h)
        ctx.rectangle(0, 0, w, h)
        ctx.set_line_width(CONFIG.image_border_width)
        levcol = CONFIG.level_colors[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        # text
        if self.ref:
            ctx.set_source_rgb(*CONFIG.osmc_colors[self.textcolor])
            layout = PangoCairo.create_layout(ctx)
            txtfont = Pango.FontDescription(CONFIG.text_font)
            layout.set_font_description(txtfont)
            layout.set_text(self.ref, -1)
            tw, th = layout.get_pixel_size()
            sc = 1.0
            if tw > w:
                sc = (float(w) - CONFIG.image_border_width)/tw
                ctx.scale(sc, sc)
            PangoCairo.update_layout(ctx, layout)
            ctx.move_to((w-sc*tw)/2, (h-sc*layout.get_iter().get_baseline()/Pango.SCALE)/2.5)
            PangoCairo.show_layout(ctx, layout)

        img.write_to_png(filename)

    def paint_bg_circle(self, ctx):
        ctx.set_line_width(0.1)
        ctx.arc(0.5, 0.5, 0.4, 0, 2*pi)
        ctx.stroke()

    def paint_bg_frame(self, ctx):
        ctx.set_line_width(0.1)
        ctx.rectangle(0.15, 0.15, 0.7, 0.7)
        ctx.stroke()

    def paint_bg_round(self, ctx):
        ctx.arc(0.5, 0.5, 0.4, 0, 2*pi)
        ctx.fill()

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

    def paint_fg_corner(self, ctx):
        ctx.move_to(0, 0)
        ctx.line_to(1, 1)
        ctx.line_to(1, 0)
        ctx.close_path()
        ctx.fill()

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
        ctx.arc(0.5, 0.5, 0.29, 0, 2*pi)
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
        ctx.set_source_rgb(*CONFIG.osmc_colors['red'])
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

    def paint_fg_hexagon(self, ctx):
        ctx.move_to(0.8, 0.5)
        ctx.line_to(0.65, 0.24)
        ctx.line_to(0.35, 0.24)
        ctx.line_to(0.2, 0.5)
        ctx.line_to(0.35, 0.76)
        ctx.line_to(0.65, 0.76)
        ctx.fill()

    def paint_fg_shell(self, ctx):
        al = ctx.get_antialias()
        #ctx.set_antialias(cairo.ANTIALIAS_NONE)
        if self.fgcolor is None:
            ctx.set_source_rgb(*CONFIG.osmc_colors['black'])
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
            ctx.set_source_rgb(*CONFIG.osmc_colors['yellow'])
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
        # XXX rewrite
        self._src_from_png(ctx, 'hiker.png')

    def paint_fg_wheel(self, ctx):
        ctx.save()
        self._src_from_png(ctx, 'red_wheel.png')

    def _src_from_png(self, ctx, name):
        ctx.save()
        src = cairo.ImageSurface.create_from_png(os.path.join(CONFIG.osmc_path, name))
        b = CONFIG.image_border_width
        ctx.scale(1.0/(src.get_width() + b), 1.0/(src.get_height() + b))
        ctx.mask_surface(src, b/2.0, b/2.0)
        ctx.restore()

class ShieldImage(object):
    """ A prerendered shield.
    """

    @classmethod
    def create(cls, tags, region, level):
        for name, stags in CONFIG.shield_names.items():
            for k,v in stags.items():
                if tags.get(k) != v:
                    break
            else:
                return cls(name, level)

        return None

    def __init__(self, name, level):
        self.shieldfile = name
        self.level = int(level/10)

    def get_id(self):
        return 'shield_%d_%s' % (self.level, self.shieldfile)

    def write_image(self, filename):
        img = cairo.ImageSurface.create_from_png(
                os.path.join(CONFIG.symbol_dir, CONFIG.shield_path,
                             "%s.png" % self.shieldfile))
        ctx = cairo.Context(img)

        # border
        ctx.rectangle(0, 0, img.get_width(), img.get_height())
        ctx.set_line_width(CONFIG.image_border_width)
        levcol = CONFIG.level_colors[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        img.write_to_png(filename)


class Slopes(object):
    """ Symbols resembling typical slope signs.
        For downhill slopes. (color from difficulty, text from ref)
    """

    @classmethod
    def create(cls, tags, region, level):
        if level > 0 and tags.get('piste:type', '') == 'downhill':
            return cls(tags, level)

    def __init__(self, tags, level):
        self.difficulty = level
        self.ref = ''

        if 'piste:ref' in tags:
            self.ref = re.sub(' ', '', tags['piste:ref'])[:3].upper()
        elif 'piste:name' in tags:
            self.ref = re.sub('[^A-Z]+', '',tags['piste:name'])[:3]
            if not self.ref:
                self.ref = re.sub(' ', '', tags['piste:name'])[:3].upper()
        elif 'ref' in tags:
            self.ref = re.sub(' ', '', tags['ref'])[:3].upper()

        if not self.ref:
            # try some magic with the name
            if 'name' in tags:
                self.ref = re.sub('[^A-Z]+', '',tags['name'])[:3]
                if not self.ref:
                    self.ref = re.sub(' ', '', tags['name'])[:3].upper()
            # must give up at this point

    def get_id(self):
        # dump ref in hex to make sure it is a valid filename
        return "slope_%d_%s" % (self.difficulty, ''.join(["%04x" % ord(x) for x in self.ref]))

    def write_image(self, filename):
        tw, th = _get_text_size(self.ref)

        # create an image where the text fits
        w, h = CONFIG.image_size
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(img)

        # background fill
        ctx.arc(w/2, h/2, w/2, 0, 2*pi)
        color = CONFIG.slope_colors[min(self.difficulty, 7)]
        ctx.set_source_rgb(*color)
        ctx.fill()
        # reference text
        ctx.set_source_rgb(*CONFIG.text_color)
        layout = PangoCairo.create_layout(ctx)
        layout.set_font_description(Pango.FontDescription(CONFIG.text_font))
        layout.set_text(self.ref, -1)
        PangoCairo.update_layout(ctx, layout)
        ctx.move_to((w-tw)/2, (h-layout.get_iter().get_baseline()/Pango.SCALE)/2.0)
        PangoCairo.show_layout(ctx, layout)

        img.write_to_png(filename)


class Nordic(object):
    """ Symbols resembling typical slope signs.
        For nordic slopes (only color from colour tag, no text).
    """

    @classmethod
    def create(cls, tags, region, level):
        if tags.get('piste:type') == 'nordic':
            color = tags.get('colour') or tags.get('color')
            if color is not None:
               cinfo = _parse_color(color)
               if cinfo is not None:
                   return cls(*cinfo)

        return None

    def __init__(self, name, color):
        self.colorname = name
        self.color = color

    def get_id(self):
        return "nordic_%s" % self.colorname

    def write_image(self, filename):
        w, h = CONFIG.image_size
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(img)
        ctx.arc(w/2, h/2, w/2, 0, 2*pi)
        ctx.set_source_rgb(*self.color)
        ctx.fill()

        img.write_to_png(filename)

class FilterRequireAny(object):
    require_any_tags = {}

    @classmethod
    def create(cls, tags, region, level):
        for k,v in cls.require_any_tags.items():
            if tags.get(k, '') == v:
                return super().create(tags, region, level)

        return None

class NorwichColorBox(FilterRequireAny, ColorBox):
    require_any_tags = {"operator" : "Norwich City Council"}

class ShieldFactory(object):

    def __init__(self, *classes):
        self.classes = [ globals()[cl] for cl in classes]

    def create(self, tags, region, level):
        """ Create a new symbol object from the given set of tags
            from a list of types.
        """
        for c in self.classes:
            sym = c.create(tags, region, level)
            if sym is not None:
                return sym

        return None

    def write(self, symbol, force=False):
        symid = symbol.get_id()

        if CONFIG.symbol_outdir is not None:
            symfn = os.path.join(CONFIG.symbol_outdir, "%s.png" % symid)
            if force or not os.path.isfile(symfn):
                symbol.write_image(symfn)

        return symid

    def create_write(self, tags, region, level, force=False):
        """ Create a new symbol object and render a picture and
            write it out.
        """
        sym = self.create(tags, region, level)

        if sym is None:
            return None

        return self.write(sym, force)



if __name__ == "__main__":
    # Testing
    import sys
    from osgende.tags import TagStore
    if len(sys.argv) != 2:
        print("Usage: python symbol.py <outdir>")
        sys.exit(-1)
    CONFIG.symbol_outdir = sys.argv[1]
    factory = ShieldFactory(
            'SwissMobile',
            'JelRef',
            'KCTRef',
            'OSMCSymbol',
            'TextSymbol',
            'Nordic',
            'Slopes',
            'ShieldImage',
            'ColorBox',
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
        ( 30, '', { 'osmc:symbol' : 'white:white:red_hexagon' }),
        ( 30, '', { 'osmc:symbol' : 'white:white_circle:yellow_triangle' }),
        ( 30, '', { 'osmc:symbol' : 'white:black_frame:blue_x' }),
        ( 30, '', { 'osmc:symbol' : 'red:white:red_diamond_line:Tk9:red' }),
        ( 0, '', { 'osmc:symbol' : 'white:blue_frame:red_dot:A' }),
        ( 10, '', { 'osmc:symbol' : 'white:red:white_bar:222' }),
        ( 10, '', { 'osmc:symbol' : 'white:red:white_bar:2223' }),
        ( 20, '', { 'osmc:symbol' : 'white:white:shell' }),
        ( 30, '', { 'osmc:symbol' : 'white:blue:shell_modern' }),
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
        ( 30, '', { 'osmc:symbol' : 'red:white:red_corner'}),
        ( 20, '', { 'osmc:symbol' : 'green:green_frame::L:green'}),
        ( 20, '', { 'osmc:symbol' : 'green:green_circle:green_dot'}),
        ( 20, '', { 'osmc:symbol' : 'green:white:green_dot'}),
        ( 20, '', { 'osmc:symbol' : 'green:red_round::A:white'}),
        ( 20, '', { 'osmc:symbol' : 'green:red_round::j:white'}),
        ( 30, '', { 'jel' : 'p+', 'ref' : 'xx'}),
        ( 30, '', { 'jel' : 'foo', 'ref' : 'yy'}),
        ( 30, '', { 'operator' : 'Norwich City Council', 'color' : '#FF0000'}),
        ( 30, '', { 'operator' : 'Norwich City Council', 'colour' : '#0000FF'}),
        ( 30, '', { 'piste:type' : 'nordic', 'colour' : '#0000FF'}),
        ( 5, '', { 'piste:type' : 'downhill', 'piste:difficulty' : 'novice'}),
    ]

    for level, region, tags in testsymbols:
        sym = factory.create_write(TagStore(tags), region, level, force=True)
