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
import xml.dom.minidom


def get_object_name_list_from_file(f):
    ids = []
    
    doc = xml.dom.minidom.parse(f)
    for node in doc.getElementsByTagName( "object" ):
        ids.append( "%s" % node.getAttribute("id") )
    
    return ids



def get_object_list_from_file(f):
    builder = gtk.Builder()
    builder.add_from_file( f )

    objs = []    
    obj_id_list = get_object_name_list_from_file( f )
    
    for obj_id in obj_id_list:
        obj_instance = builder.get_object( obj_id )
        obj_instance.set_data( "ide-builder-id", obj_id )
        objs.append( obj_instance )
    
    return objs


def get_object_name(obj):
    # gtk.Buildable.get_name( obj ): only works for widgets.
    # what about non-widgets? that's why we must have our own scheme.
    #

    try:
        return obj.get_data( "ide-builder-id" )
    except:
        return "untitled_" + str(hash(obj))

