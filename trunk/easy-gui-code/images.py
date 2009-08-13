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

import gtk
import os.path


class Images:

    img_names = ( \
        'signal_default', \
        'signal_event', \
        'signal_parent', \

        'prop_default', \
        'prop_int', \
        'prop_bool', \
        'prop_string', \
        'prop_float', \
        'prop_color', \

        'close'
    )


    def __init__(self):
        self.imgs = {}

        for f in self.img_names:
            filename = os.path.join( os.path.dirname(__file__), \
                "imgs", "etc", f + ".png" )
            self.imgs[f] = gtk.gdk.pixbuf_new_from_file( filename )


    def by_name(self, image_name):
        return self.imgs[ image_name ]
