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


def is_non_widget_but_important(obj):
    return \
        type(obj) == gtk.Adjustment or \
        type(obj) == gtk.ListStore or \
        type(obj) == gtk.TreeStore

    
def is_container_object(obj):
    return \
        type(obj) == gtk.HBox or \
        type(obj) == gtk.VBox or \
        type(obj) == gtk.HButtonBox or \
        type(obj) == gtk.VButtonBox or \
        type(obj) == gtk.Table or \
        type(obj) == gtk.HPaned or \
        type(obj) == gtk.VPaned or \
        type(obj) == gtk.Expander or \
        type(obj) == gtk.Alignment or \
        type(obj) == gtk.Fixed or \
        type(obj) == gtk.HSeparator or \
        type(obj) == gtk.VSeparator


def is_basic_object(obj):
    return is_non_widget_but_important(obj) or isinstance(obj, gtk.Widget)

