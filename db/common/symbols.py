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
from math import pi
from xml.dom.minidom import parse
from xml.parsers.expat import ExpatError

import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
gi.require_version('Rsvg', '2.0')
from gi.repository import Pango, PangoCairo, Rsvg

from db.common.route_types import Network
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

def _parse_ref(tags):
    if 'ref' in tags:
        return re.sub(' ', '', tags['ref'])[:5]

    # try some magic with the name
    name = tags.get('name') or tags.get('osmc:name')
    if name is None:
        return None

    if len(name) <= 5:
        return name

    ref = re.sub('[^A-Z]+', '', name)[:3]
    if len(ref) < 2:
        ref = re.sub(' ', '', name)[:3]

    return ref

def _get_text_size(text):
    # get text size
    txtctx_layout = PangoCairo.create_layout(
                       cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 10,10)))
    txtfont = Pango.FontDescription(CONFIG.text_font)
    txtctx_layout.set_font_description(txtfont)
    txtctx_layout.set_text(text, -1)
    return txtctx_layout.get_pixel_size()

def _encode_ref(ref):
    return ''.join(["%04x" % ord(x) for x in ref])

def make_surface(filename, w, h):
    img = cairo.SVGSurface(filename, w, h)
    major, minor, patch = cairo.version_info
    if major == 1 and minor >= 18:
        img.set_document_unit(cairo.SVGUnit.PX)

    return img

class ColorBox(object):
    """ Creates an unmarked colored box according to the color tag.
    """
    @classmethod
    def create(cls, tags, region, level):
        color = tags.firstof('color', 'colour')
        if color is not None:
            cinfo = _parse_color(color)
            if cinfo is not None:
                return cls(level, cinfo[0], cinfo[1])

        return None

    def __init__(self, level, name, color):
        self.level = Network.from_int(level)
        self.color = color
        self.colorname = name


    def get_id(self):
        return "cbox_%d_%s" % (self.level.value, self.colorname)

    def write_image(self, filename):
        w, h = CONFIG.image_size

        # create an image where the text fits
        img = make_surface(filename, w, h)
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

        ctx.show_page()

class TextColorBelow(object):
    """ Creates a textbox with a colored underline
    """
    @classmethod
    def create(cls, tags, region, level):
        ref = _parse_ref(tags)
        color = tags.firstof('color', 'colour')
        if ref is not None and color is not None:
            if color in CONFIG.colorbox_names:
                return cls(level, ref, color, CONFIG.colorbox_names[color])

            cinfo = _parse_color(color)
            if cinfo is not None:
                return cls(level, ref, cinfo[0], (cinfo[1], (1., 1., 1.)))

        return None

    def __init__(self, level, ref, name, color):
        self.level = Network.from_int(level)
        self.ref = ref
        self.color = color
        self.colorname = name


    def get_id(self):
        return "ctb_%d_%s_%s" % (self.level.value, _encode_ref(self.ref),
                                 self.colorname)

    def write_image(self, filename):
        # get text size
        tw, th = _get_text_size(self.ref)

        # create an image where the text fits
        w = int(tw + CONFIG.text_border_width + 2 * CONFIG.image_border_width)
        h = int(CONFIG.image_size[1] + CONFIG.image_border_width)
        img = make_surface(filename, w, h)
        ctx = cairo.Context(img)

        # background fill
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # bar with halo
        ctx.set_line_width(0)
        ctx.set_source_rgb(*self.color[1])
        ctx.rectangle(CONFIG.image_border_width + 1.8, h - 3.2 - CONFIG.image_border_width,
                      w - 2 * (CONFIG.image_border_width + 1.8) , 3.4)
        ctx.fill()
        ctx.set_source_rgb(*self.color[0])
        ctx.rectangle(CONFIG.image_border_width + 2, h - 3 - CONFIG.image_border_width,
                      w - 2 * (CONFIG.image_border_width + 2) , 3)
        ctx.fill()

        # border
        ctx.rectangle(0, 0, w, h)
        ctx.set_line_width(CONFIG.image_border_width)
        levcol = CONFIG.level_colors[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        # reference text
        ctx.set_source_rgb(*CONFIG.text_color)
        layout = PangoCairo.create_layout(ctx)
        layout.set_font_description(Pango.FontDescription(CONFIG.text_font))
        layout.set_text(self.ref, -1)
        PangoCairo.update_layout(ctx, layout)
        ctx.move_to((w-tw)/2, (h-layout.get_iter().get_baseline()/Pango.SCALE)/2.0 - 3)
        PangoCairo.show_layout(ctx, layout)

        ctx.show_page()

class ItalianHikingRefs(object):
    """ Special rendering for Italian CAI.
    """
    @classmethod
    def create(cls, tags, region, level):
        osmc = re.match('red:red:white_(bar|stripe):([0-9a-zA-Z]+):black', tags.get('osmc:symbol', ''))

        if osmc and region == 'it':
            redway = level >= 30 and 'cai_scale' in tags
            return cls(None if redway else Network.from_int(level),
                       osmc.group(1), osmc.group(2))

        return None

    def __init__(self, level, typ, ref):
        self.level = level
        self.typ = typ
        self.ref = ref

    def get_id(self):
        if self.level is None:
            return "cai_red_%s_%s" % (self.typ, self.ref)
        else:
            return "cai_%d_%s_%s" % (self.level.value, self.typ, self.ref)

    def write_image(self, filename):
        # get text size
        tw, th = _get_text_size(self.ref)

        # create an image where the text fits
        w = int(tw + 2 * CONFIG.cai_border_width)
        h = int(CONFIG.image_size[1] + 0.5 * CONFIG.cai_border_width)
        w = max(h, w)
        img = make_surface(filename, w, h)
        ctx = cairo.Context(img)

        # background fill
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # bars
        ctx.set_source_rgb(*CONFIG.osmc_colors['red'])
        ctx.rectangle(0, 0, w, h)
        ctx.set_line_width(CONFIG.image_border_width)
        ctx.stroke()

        ctx.set_line_width(0)
        if self.typ == 'stripe':
            ctx.rectangle(0, 0, CONFIG.cai_border_width, h)
            ctx.fill()
            ctx.rectangle(w - CONFIG.cai_border_width, 0, CONFIG.cai_border_width, h)
            ctx.fill()
        else:
            ctx.rectangle(0, 0, w, 0.9 * CONFIG.cai_border_width)
            ctx.fill()
            ctx.rectangle(0, h - 0.9 * CONFIG.cai_border_width, w, 0.9 * CONFIG.cai_border_width)
            ctx.fill()

        # border
        ctx.rectangle(0, 0, w, h)
        if self.level is None:
            levcol = (255, 0, 0)
            ctx.set_line_width(0.5 * CONFIG.image_border_width)
        else:
            levcol = CONFIG.level_colors[self.level]
            ctx.set_line_width(0.8 * CONFIG.image_border_width)
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        # reference text
        ctx.set_source_rgb(*CONFIG.text_color)
        layout = PangoCairo.create_layout(ctx)
        layout.set_font_description(Pango.FontDescription(CONFIG.text_font))
        layout.set_text(self.ref, -1)
        PangoCairo.update_layout(ctx, layout)
        y = (h-layout.get_iter().get_baseline()/Pango.SCALE)/2.0
        if self.typ == 'bar':
            y -= 1
        ctx.move_to((w-tw)/2, y)
        PangoCairo.show_layout(ctx, layout)

        ctx.show_page()


class TextSymbol(object):
    """A simple symbol only displaying a reference.

       If a ref tag is found, it will be used for the shield name. Otherwise,
       a pseudo reference is derived from the name by first trying all
       major letters and if that doesn't help the first part of the name.

       Font, size and color of the text can be configured in :mod:`conf`.
    """

    @classmethod
    def create(cls, tags, region, level):
        ref = _parse_ref(tags)
        # must give up at this point
        if not ref:
            return None

        return cls(ref, level)

    def __init__(self, ref, level):
        self.level = Network.from_int(level)
        self.ref = ref


    def get_id(self):
        # dump ref in hex to make sure it is a valid filename
        return "ref_%d_%s" % (self.level.value, _encode_ref(self.ref))

    def write_image(self, filename):
        # get text size
        tw, th = _get_text_size(self.ref)

        # create an image where the text fits
        w = int(tw + CONFIG.text_border_width + 2 * CONFIG.image_border_width)
        h = CONFIG.image_size[1]
        img = make_surface(filename, w, h)
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
        ctx.move_to((w-tw)/2, (h-CONFIG.text_border_width-layout.get_iter().get_baseline()/Pango.SCALE)/2.0)
        PangoCairo.show_layout(ctx, layout)

        ctx.show_page()

class SwissMobile(object):
    """Symboles for Swiss Mobile networks
    """

    @classmethod
    def create(cls, tags, region, level):
        if 'ref' in tags \
           and tags.get('operator', '').lower() in CONFIG.swiss_mobile_operators \
           and tags.get('network', '') in CONFIG.swiss_mobile_networks:
            return cls(tags['ref'], level)

        return None

    def __init__(self, ref, level):
        self.ref = ref.strip()[:5]
        self.level = Network.from_int(level)

    def get_id(self):
        return 'swiss_%s' % ''.join(["%04x" % ord(x) for x in self.ref])

    def write_image(self, filename):
        w = 8 + len(self.ref)*7
        h = CONFIG.image_size[1]

        # create an image where the text fits
        img = make_surface(filename, w, h)
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

        ctx.show_page()

class JelRef(object):
    """Hiking symbols used in Hungary. (tag jel)
    """

    @classmethod
    def create(cls, tags, region, level):
        if 'jel'in tags and tags['jel'] in CONFIG.jel_types:
            return cls(tags['jel'], level)

        return None

    def __init__(self, symbol, level):
        self.level = Network.from_int(level)
        self.symbol = symbol

    def get_id(self):
        return 'jel_%d_%s' % (self.level.value, self.symbol)

    def write_image(self, filename):
        w, h = CONFIG.image_size
        img = make_surface(filename, w, h)
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
        ctx.rectangle(0, 0, w, h)
        ctx.set_line_width(CONFIG.image_border_width)
        levcol = CONFIG.level_colors[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        ctx.show_page()

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
        self.level = Network.from_int(level)
        self.color = color
        self.symbol = symbol

    def get_id(self):
        return 'kct_%d_%s-%s' % (self.level.value, self.color, self.symbol)

    def write_image(self, filename):
        fn = os.path.join(CONFIG.symbol_dir, CONFIG.kct_path, "%s.svg" % self.symbol)
        with open(fn, 'r') as fd:
            content = fd.read()
        fgcol = tuple([int(x*255) for x in CONFIG.kct_colors[self.color]])
        color = '#%02x%02x%02x' % fgcol
        content = re.sub('#eeeeee', color, content)
        svg = Rsvg.Handle.new_from_data(content.encode())

        dim = svg.get_dimensions()

        w, h = CONFIG.image_size
        w, h = w + 0.5 * CONFIG.image_border_width, h + 0.5 * CONFIG.image_border_width
        img = make_surface(filename, w, h)
        ctx = cairo.Context(img)
        ctx.scale(w/dim.width, h/dim.height)
        svg.render_cairo(ctx)

        # border
        ctx.scale(dim.width/w, dim.height/h)
        ctx.rectangle(0, 0, w, h)
        ctx.set_line_width(CONFIG.image_border_width)
        levcol = CONFIG.level_colors[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        ctx.show_page()

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
        self.level = Network.from_int(level)
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
                        self.textcolor = parts[4].strip()
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
        if symbol != "red_diamond" and hasattr(self, 'paint_fg_' + symbol):
            self.fgsymbol = symbol
            self.fgcolor = 'yellow' if symbol.startswith('shell') else 'black'
        else:
            idx = symbol.find('_')
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
            return 'osmc_%d_%s_%s_%s_%s' % (
                    self.level.value, bg, fg,
                    _encode_ref(self.ref), self.textcolor)
        else:
            return "osmc_%d_%s_%s" % (self.level.value, bg, fg)

    def write_image(self, filename):
        if len(self.ref) <= 2:
            w, h = CONFIG.image_size
        else:
            w, h = CONFIG.wide_image_size
        if self.ref:
            h = int(h + CONFIG.image_border_width)
            w = int(w + CONFIG.image_border_width)

        # create an image where the text fits
        img = make_surface(filename, w, h)
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

        if self.bgsymbol is not None:
            ctx.set_source_rgb(*CONFIG.osmc_colors[self.bgcolor])
            func = getattr(self, 'paint_bg_' + self.bgsymbol)
            func(ctx)

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
            if tw > w - CONFIG.image_border_width:
                sc = (float(w) - 1.5 * CONFIG.image_border_width)/tw
                ctx.scale(sc, sc)
            PangoCairo.update_layout(ctx, layout)
            ctx.move_to((w/sc-tw)/2.0, (h/sc-th)/2.0)
            PangoCairo.show_layout(ctx, layout)

        ctx.show_page()

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
        ctx.rectangle(0, 0.5, 1, 0.5)
        ctx.fill()

    def paint_fg_right(self, ctx):
        ctx.rectangle(0.5, 0, 0.5, 1)
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
        self._src_from_svg(ctx, 'hiker.svg')

    def paint_fg_wheel(self, ctx):
        ctx.save()
        self._src_from_svg(ctx, 'wheel.svg')

    def _src_from_svg(self, ctx, name):
        fn = os.path.join(CONFIG.symbol_dir, CONFIG.osmc_path, name)
        if self.fgcolor is None:
            svg = Rsvg.Handle.new_from_file(fn)
        else:
            with open(fn, 'r') as fd:
                content = fd.read()
            fgcol = tuple([int(x*255) for x in CONFIG.osmc_colors[self.fgcolor]])
            color = '#%02x%02x%02x' % fgcol
            content = re.sub('#000000', color, content)
            svg = Rsvg.Handle.new_from_data(content.encode())

        w, h = CONFIG.image_size
        b = CONFIG.image_border_width
        bw, bh = b/w, b/h

        ctx.save()
        ctx.translate(bw, bh)
        ctx.scale((1.0 - 2.0*bw)/svg.props.width, (1.0 - 2.0*bh)/svg.props.height)
        svg.render_cairo(ctx)
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
        self.level = Network.from_int(level)

    def get_id(self):
        return 'shield_%d_%s' % (self.level.value, self.shieldfile)

    def write_image(self, filename):
        path = os.path.join(CONFIG.symbol_dir, CONFIG.shield_path, "%s.svg" % self.shieldfile)
        svg = Rsvg.Handle.new_from_file(path)
        dim = svg.get_dimensions()

        img = make_surface(filename, dim.width, dim.height)
        ctx = cairo.Context(img)
        svg.render_cairo(ctx)

        # border
        ctx.rectangle(0, 0, dim.width, dim.height)
        ctx.set_line_width(CONFIG.image_border_width)
        levcol = CONFIG.level_colors[self.level]
        ctx.set_source_rgb(*levcol)
        ctx.stroke()

        ctx.show_page()


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
        return "slope_%d_%s" % (self.difficulty, _encode_ref(self.ref))

    def write_image(self, filename):
        tw, th = _get_text_size(self.ref)

        # create an image where the text fits
        w, h = CONFIG.image_size
        img = make_surface(filename, w, h)
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

        ctx.show_page()


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
        img = make_surface(filename, w, h)
        ctx = cairo.Context(img)
        ctx.arc(w/2, h/2, w/2, 0, 2*pi)
        ctx.set_source_rgb(*self.color)
        ctx.fill()

        ctx.show_page()

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
            symfn = os.path.join(CONFIG.symbol_outdir, "%s.svg" % symid)
            if force or not os.path.isfile(symfn):
                symbol.write_image(symfn)
                self._mangle_svg(symfn)


        return symid

    def create_write(self, tags, region, level, force=False):
        """ Create a new symbol object and render a picture and
            write it out.
        """
        sym = self.create(tags, region, level)

        if sym is None:
            return None

        return self.write(sym, force)

    def _mangle_svg(self, filename):
        try:
            dom = parse(filename)
        except ExpatError:
            print("WARNING: cannot parse", filename)
            return

        for svg in dom.getElementsByTagName("svg"):
            sym_ele = svg.getElementsByTagName("symbol")
            use_ele = svg.getElementsByTagName("use")

            if sym_ele.length == 0 or use_ele.length == 0:
                continue

            symbols = {}
            for e in sym_ele:
                symbols['#' + e.getAttribute('id')] = e.cloneNode(True)
                e.parentNode.removeChild(e)

            for e in use_ele:
                ref = e.getAttribute('xlink:href')
                x   = float(e.getAttribute('x'))
                y   = float(e.getAttribute('y'))

                group = dom.createElement('g')

                for ce in symbols[ref].childNodes:
                    node = ce.cloneNode(True)

                    if node.nodeName == 'path':
                        path = node.getAttribute('d')

                        newpath = ''
                        is_x = True
                        for p in path.split():
                            if not p:
                                continue

                            if p[0].isupper():
                                dx = x
                                dy = y
                                newpath += p + ' '
                            elif p[0].islower():
                                dx = 0
                                dy = 0
                                newpath += p + ' '
                            elif p[0].isnumeric:
                                val = float(p) + (dx if is_x else dy)
                                is_x = not is_x
                                newpath += "%f " % val

                        node.setAttribute('d', newpath)

                    group.appendChild(node)

                e.parentNode.replaceChild(group, e)

        with open(filename, 'w') as of:
            dom.writexml(of)


if __name__ == "__main__":
    import sys
    from osgende.common.tags import TagStore
    if len(sys.argv) < 2:
        print("Usage: python symbol.py [--create-osmc-legend] <outdir>")
        sys.exit(-1)
    factory = ShieldFactory(
            'SwissMobile',
            'JelRef',
            'KCTRef',
            'ItalianHikingRefs',
            'OSMCSymbol',
            'Nordic',
            'Slopes',
            'ShieldImage',
            'TextColorBelow',
            'ColorBox',
            'TextSymbol',
        )

    if sys.argv[1] == '--create-osmc-legend':
        CONFIG.level_colors = [(0.1, 0.1, 0.1) for x in Network]
        CONFIG.image_border_width = 1.5
        for col in CONFIG.osmc_colors.keys():
            sym = OSMCSymbol.create({ 'osmc:symbol' : 'red:' + col }, '', 0)
            sym.write_image(os.path.join(sys.argv[2], 'background', col + '.svg'))
        for k in OSMCSymbol.__dict__.keys():
            if k.startswith('paint_bg_'):
                for col in CONFIG.osmc_colors.keys():
                    osmcbg = "%s_%s" % (col, k[9:])
                    sym = OSMCSymbol.create({ 'osmc:symbol' : 'red:' + osmcbg },
                                            '', 30)
                    sym.write_image(os.path.join(sys.argv[2], 'background', osmcbg + '.svg'))
            elif k.startswith('paint_fg_'):
                sym = OSMCSymbol.create({ 'osmc:symbol' : 'red:white:' + k[9:] }, '', 30)
                sym.write_image(os.path.join(sys.argv[2], 'foreground', k[9:] + '.svg'))
                for col in CONFIG.osmc_colors.keys():
                    osmcfg = "%s_%s" % (col, k[9:])
                    if col == 'white':
                        osmc = 'red:black:' + osmcfg
                    else:
                        osmc = 'red:white:' + osmcfg
                    sym = OSMCSymbol.create({ 'osmc:symbol' : osmc },
                                            '', 30)
                    sym.write_image(os.path.join(sys.argv[2], 'foreground', osmcfg + '.svg'))
        sys.exit(0)
    # Testing
    CONFIG.symbol_outdir = sys.argv[1]
    testsymbols = [
        (Network.INT(), '', { 'ref' : '10' }),
        (Network.LOC(), '', { 'ref' : '15' }),
        (Network.REG(), '', { 'ref' : 'WWWW' }),
        (Network.NAT(), '', { 'ref' : '1' }),
        (Network.REG(), '', { 'ref' : 'Ag' }),
        (Network.REG(), '', { 'ref' : u'１号路' }),
        (Network.REG(), '', { 'ref' : u'يلة' }),
        (Network.REG(), '', { 'ref' : u'하이' }),
        (Network.REG(), '', { 'ref' : u'шие' }),
        (Network.NAT(), '', { 'ref' : '7', 'operator' : 'swiss mobility', 'network' : 'nwn'}),
        (Network.REG(), '', { 'ref' : '57', 'operator' : 'swiss mobility', 'network' : 'rwn'}),
        (Network.REG(), '', { 'operator' : 'kst', 'symbol' : 'learning', 'colour' : 'red'}),
        (Network.INT(), '', { 'osmc:symbol' : 'red::blue_lower' }),
        (Network.INT(), '', { 'osmc:symbol' : 'white:white:blue_lower' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_arch' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_backslash' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_bar' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_circle' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_cross' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_diamond_line' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:red_diamond' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_dot' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_fork' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_pointer' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_rectangle_line' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_rectangle' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_red_diamond' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_slash' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_stripe' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_triangle_line' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_triangle' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_triangle_turned' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_turned_T' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:blue_x' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:red_hexagon' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white_circle:yellow_triangle' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:black_frame:blue_x' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:red_frame:black_corner' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:red_circle:black_corner' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'red:white:red_diamond_line:Tk9:red' }),
        (Network.INT(), '', { 'osmc:symbol' : 'white:blue_frame:red_dot:A' }),
        (Network.NAT(), '', { 'osmc:symbol' : 'white:red:white_bar:222' }),
        (Network.NAT(), '', { 'osmc:symbol' : 'white:red:white_bar:2223' }),
        (Network.REG(), '', { 'osmc:symbol' : 'white:white:shell' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:blue:shell_modern' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:white:hiker' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white::green_hiker' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white::blue_hiker' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white::blue_wheel' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white::red_wheel' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white::wheel' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:brown:white_triangle' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:gray:purple_fork' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:green:orange_cross' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:orange:black_lower' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:orange:black_right' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:purple:green_turned_T' }),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:red:gray_stripe'}),
        (Network.LOC(), '', { 'osmc:symbol' : 'white:yellow:brown_diamond_line'}),
        (Network.LOC(), '', { 'osmc:symbol' : 'red:white:red_wheel'}),
        (Network.LOC(), '', { 'osmc:symbol' : 'red:white:red_corner'}),
        (Network.REG(), '', { 'osmc:symbol' : 'green:green_frame::L:green'}),
        (Network.REG(), '', { 'osmc:symbol' : 'green:green_circle:green_dot'}),
        (Network.REG(), '', { 'osmc:symbol' : 'green:white:green_dot'}),
        (Network.REG(), '', { 'osmc:symbol' : 'green:red_round::A:white'}),
        (Network.REG(), '', { 'osmc:symbol' : 'green:red_round::j:white'}),
        (Network.REG(), '', { 'osmc:symbol' : 'blue:white::Lau:blue'}),
        (Network.NAT(), '', { 'osmc:symbol' : 'yellow:brown_round:red_dot'}),
        (Network.LOC(), 'it', { 'osmc:symbol' : 'red:red:white_bar:223:black'}),
        (Network.LOC(), 'it', { 'osmc:symbol' : 'red:red:white_stripe:1434:black'}),
        (Network.LOC(), 'it', { 'osmc:symbol' : 'red:red:white_stripe:1:black'}),
        (Network.LOC(), 'it', { 'osmc:symbol' : 'red:red:white_bar:1:black'}),
        (Network.LOC(), 'it', { 'osmc:symbol' : 'red:red:white_bar:26:black'}),
        (Network.LOC(), 'it', { 'osmc:symbol' : 'red:red:white_stripe:26:black'}),
        (Network.LOC(), 'it', { 'osmc:symbol' : 'red:red:white_stripe:26s:black'}),
        (Network.REG(), 'it', { 'osmc:symbol' : 'red:red:white_stripe:AVG:black'}),
        (Network.LOC(), '', { 'jel' : 'p+', 'ref' : 'xx'}),
        (Network.LOC(), '', { 'jel' : 'foo', 'ref' : 'yy'}),
        (Network.LOC(), '', { 'kct_red' : 'major'}),
        (Network.LOC(), '', { 'kct_green' : 'interesting_object'}),
        (Network.LOC(), '', { 'kct_yellow' : 'ruin'}),
        (Network.LOC(), '', { 'kct_blue' : 'spring'}),
        (Network.LOC(), '', { 'operator' : 'Norwich City Council', 'color' : '#FF0000'}),
        (Network.LOC(), '', { 'operator' : 'Norwich City Council', 'colour' : '#0000FF'}),
        (Network.LOC(), '', { 'ref' : '123', 'colour' : 'yellow'}),
        (Network.NAT(), '', { 'ref' : 'KCT', 'colour' : 'blue'}),
        (Network.NAT(), '', { 'ref' : 'YG4E3', 'colour' : 'green'}),
        (Network.NAT(), '', { 'ref' : 'XXX', 'colour' : 'aqua'}),
        (Network.NAT(), '', { 'ref' : 'XXX', 'colour' : 'black'}),
        (Network.NAT(), '', { 'ref' : 'XXX', 'colour' : 'blue'}),
        (Network.NAT(), '', { 'ref' : 'XXX', 'colour' : 'brown'}),
        (Network.NAT(), '', { 'ref' : 'XXX', 'colour' : 'green'}),
        (Network.NAT(), '', { 'ref' : 'X/XX', 'colour' : 'grey'}),
        (Network.NAT(), '', { 'ref' : 'XXX', 'colour' : 'maroon'}),
        (Network.NAT(), '', { 'ref' : 'XXX', 'colour' : 'orange'}),
        (Network.NAT(), '', { 'ref' : 'XXX', 'colour' : 'pink'}),
        (Network.NAT(), '', { 'ref' : 'XXX', 'colour' : 'purple'}),
        (Network.NAT(), '', { 'ref' : 'XXX', 'colour' : 'red'}),
        (Network.NAT(), '', { 'ref' : 'XXX', 'colour' : 'violet'}),
        (Network.NAT(), '', { 'ref' : 'XXX', 'colour' : 'white'}),
        (Network.NAT(), '', { 'ref' : 'XXX', 'colour' : 'yellow'}),
        (10, '', { 'piste:type' : 'nordic', 'colour' : '#0000FF'}),
        (5, '', { 'piste:type' : 'downhill', 'piste:difficulty' : 'novice'}),
    ]

    for level, region, tags in testsymbols:
        sym = factory.create_write(TagStore(tags), region, level, force=True)
