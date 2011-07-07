#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
#
# Copyright (C) 2009, 2011 Ricardo Lenz
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
#


import os
import gtk
import cairo
import xml.dom.minidom



PI = 3.14159265




def build_path(*args):
    app_dir = os.path.dirname(__file__)
    s = os.path.join( *args )
    return os.path.join( app_dir, s )



def alert(msg, title = "Easy GUI Code"):
    dlg = gtk.MessageDialog( type = gtk.MESSAGE_INFO, buttons = gtk.BUTTONS_OK )
    dlg.set_title( title )
    dlg.set_markup( msg )
    dlg.run()
    dlg.destroy()
    




class Images:
    img_names = ( 'signal_default', 'signal_event', 'signal_parent', \
        'prop_default', 'prop_int', 'prop_bool', 'prop_string', \
        'prop_float', 'prop_color', 'title_bar_btn', 'title_bar_icon' )

    def __init__(self):
        self.imgs = {}
        for f in self.img_names:
            filename = build_path( "imgs", "etc", f + ".png" )
            self.imgs[f] = gtk.gdk.pixbuf_new_from_file( filename )

        self.obj_imgs = {}
        obj_imgs = os.listdir( build_path( "imgs", "objects" ) )
        for obj_img in obj_imgs:
            if obj_img[-3:].lower() != "png": continue
            obj_name = obj_img[:-4]
            filename = build_path( "imgs", "objects", obj_img )
            self.obj_imgs[ obj_name ] = gtk.gdk.pixbuf_new_from_file( filename )


images_instance = None
def get_images_instance():
    global images_instance
    if images_instance == None:
        images_instance = Images()
    return images_instance

def get_image_by_name(name):
    return get_images_instance().imgs[name]

def get_object_image_by_name(obj_name):
    imgs = get_images_instance()
    if obj_name in imgs.obj_imgs:
        return imgs.obj_imgs[ obj_name ]
    else:
        return None 





def is_non_widget_important(obj):
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
    return is_non_widget_important(obj) or isinstance(obj, gtk.Widget)








########################################################################3
#
# gtk.Buildable.get_name( obj ): only works for widgets.
# and what about non-widgets?
# that's why we must have our own scheme here.
#
#
#
def get_object_names_from_glade_file(f):
    ids = []
    doc = xml.dom.minidom.parse(f)
    for node in doc.getElementsByTagName( "object" ):
        ids.append( "%s" % node.getAttribute("id") )
    return ids


def get_objects_with_names_from_glade_file(f):
    builder = gtk.Builder()
    builder.add_from_file( f )

    objs = []    
    obj_id_list = get_object_names_from_glade_file( f )
    
    for obj_id in obj_id_list:
        obj_instance = builder.get_object( obj_id )
        obj_instance.set_data( "easy-gui-code-obj-id", obj_id )
        objs.append( obj_instance )
    return objs


def get_object_name(obj):
    try:
        return obj.get_data( "easy-gui-code-obj-id" )
    except:
        return "untitled_" + str(hash(obj))

#
#
#
#############################################







def hex_to_rgb(h):
    if h[0] == '#': h = h[1:]
    r = float( int( h[0:2], 16 ) ) / 255
    g = float( int( h[2:4], 16 ) ) / 255
    b = float( int( h[4:6], 16 ) ) / 255
    return r,g,b


def cairo_rounded_rect(cr, x, y, w, h, radius_x=5, radius_y=5):

    # fonte:
    # http://graphics.stanford.edu/courses/cs248-98-fall/Final/q1.html

    ARC_TO_BEZIER = 0.55228475
    if radius_x > w - radius_x: radius_x = w / 2
    if radius_y > h - radius_y: radius_y = h / 2

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

