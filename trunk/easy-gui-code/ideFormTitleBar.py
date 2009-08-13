#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2009 Ricardo Lenz
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import cairo


def rounded_rec(cr, x, y, w, h, radius_x=5, radius_y=5):

    #from mono moonlight aka mono silverlight
    #test limits (without using multiplications)
    # http://graphics.stanford.edu/courses/cs248-98-fall/Final/q1.html

    ARC_TO_BEZIER = 0.55228475
    if radius_x > w - radius_x:
        radius_x = w / 2
    if radius_y > h - radius_y:
        radius_y = h / 2


    #approximate (quite close) the arc using a bezier curve
    c1 = ARC_TO_BEZIER * radius_x
    c2 = ARC_TO_BEZIER * radius_y

    cr.new_path();
    cr.move_to ( x + radius_x, y)
    cr.rel_line_to ( w - 2 * radius_x, 0.0)
    cr.rel_curve_to ( c1, 0.0, radius_x, c2, radius_x, radius_y)
    cr.rel_line_to ( 0, h - 2 * radius_y)
    cr.rel_curve_to ( 0.0, c2, c1 - radius_x, radius_y, -radius_x, radius_y)
    cr.rel_line_to ( -w + 2 * radius_x, 0)
    cr.rel_curve_to ( -c1, 0, -radius_x, -c2, -radius_x, -radius_y)
    cr.rel_line_to (0, -h + 2 * radius_y)
    cr.rel_curve_to (0.0, -c2, radius_x - c1, -radius_y, radius_x, -radius_y)
    cr.close_path ()




def draw_titlebar(cr, w, h, close_button):

    r = 0.36
    g = 0.52
    b = 0.72
    dif = 0.1
    alpha = 1.0

    grad = cairo.LinearGradient( 0, 0, 0, h )
    grad.add_color_stop_rgba( 0.0,   r+dif, g+dif, b+dif, alpha )
    grad.add_color_stop_rgba( 1.0,   r-dif, g-dif, b-dif, alpha )

    cr.set_source( grad )
    rounded_rec( cr, 0, 0, w-1, h * 2 )
    cr.fill()

    cr.set_line_width( 1 )
    cr.set_source_rgb( 0, 0, 0 )
    rounded_rec( cr, 0 + 0.5, 0 + 0.5, w-1, h * 2 )
    cr.move_to( 0 + 0.5, h-1 + 0.5 )
    cr.line_to( w-1 + 0.5, h-1 + 0.5 )
    cr.stroke()

    bw = close_button.get_width()
    bh = close_button.get_height()

    cr.translate( w - bw - 8, 8 )
    cr.set_source_pixbuf( close_button, 0, 0 )
    cr.paint()
    cr.fill()

    cr.set_source_rgba( 0, 0, 0, 0.5 )
    rounded_rec( cr, -3 + 0.5, -3 + 0.5, bw + 5, bh + 5, 3, 3 )
    cr.stroke()
