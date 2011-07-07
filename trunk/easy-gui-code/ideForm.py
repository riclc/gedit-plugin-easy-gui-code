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
import cairo

from utils import *


TITLE_BAR_COLOR_TOP = '#787772'
TITLE_BAR_COLOR_BOTTOM = '#3c3b37'
TITLE_BAR_BTN_RIGHT = 9
TITLE_BAR_BTN_TOP = 5
TITLE_BAR_ICON_LEFT = 11
TITLE_BAR_ICON_TOP = 5

SELECT_BORDER_COLOR1 = '#68402e'
SELECT_BORDER_COLOR2 = '#b79150'
SELECT_BORDER_WIDTH_SET   = 1
SELECT_BORDER_WIDTH_OVER  = 2
SELECT_BORDER_DASH_SET    = [4, 2]
SELECT_BORDER_DASH_OVER   = [4, 2]
SELECT_BORDER_ALPHA_SET   = 1.0
SELECT_BORDER_ALPHA_OVER  = 0.3


class FormControls:
    pass


class ControlArea:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.size = 0 * 0
        self.ctrl = None


class Form:
    def __init__(self, ide):
        self.ctrl_over = None
        self.ctrl_selected = None

        self.screenshot = None
        self.main_window = None
        self.areas = []

        self.img_title_bar_btn = get_image_by_name( "title_bar_btn" )
        self.img_title_bar_icon = get_image_by_name( "title_bar_icon" )

        self.ide = ide



    def load_from_file(self, glade_filename):
        self.formControls = FormControls()
        self.formControls.objs = get_objects_with_names_from_glade_file( glade_filename )
        self.read_objects()
        self.config_objects()
    
    
    def read_objects(self):
        self.ide.storeObjects.clear()
        ordered_objs = []
        
        for obj in self.formControls.objs:
            tobj = "gtk." + obj.__class__.__name__
            obj_name = get_object_name( obj )

            setattr( self.formControls, obj_name, obj )
            desc_obj = "<b>%s</b> (%s)" % (obj_name, tobj)
            
            if is_basic_object( obj ):
                if not is_container_object(obj) or self.ide.checkContainers.get_active():
                    ordered_objs.append( [obj_name, obj, desc_obj] )

            if isinstance( obj, gtk.Window ): self.main_window = obj
        
        ordered_objs.sort()
        for item in ordered_objs:
            obj_name, obj, desc_obj = item[0], item[1], item[2]
            self.ide.storeObjects.append( [None, desc_obj, obj, obj_name] )



    def config_objects(self):
        if self.main_window == None:
            print("*** No window found in the glade file!")
            return

        # define a aparencia do form
        #
        titulo = self.main_window.get_title()
        if titulo == None: titulo = "Form1"
        self.ide.formTitle.set_text( titulo )
        
        w, h = self.main_window.get_size()
        h += self.ide.formTitleBar.get_size_request()[1]
        self.ide.formFrame.set_size_request( w, h )

        self.capture_screenshot()

        self.ide.formBox.connect( "motion-notify-event", self.on_mouse_move )
        self.ide.formBox.connect( "button-press-event", self.on_mouse_button_press )
        self.ide.formContainer.connect( "expose-event", self.on_expose )



    def capture_screenshot(self):
        ow = gtk.OffscreenWindow()
        self.main_window.get_child().reparent( ow )
        ow.show()        
        ow.window.process_updates( update_children=True )
        self.screenshot = ow.get_pixbuf()

        ####
        
        self.areas = []
        for obj in self.formControls.objs:
            if isinstance( obj, gtk.Widget ):
                a = obj.get_allocation()

                area = ControlArea()
                area.x = a.x
                area.y = a.y
                area.w = a.width
                area.h = a.height
                area.ctrl = obj
                area.size = area.w * area.h
                self.areas.append( area )



    def get_control_at(self, x, y):
        menor_size = 0
        menor_size_ctrl = None

        for area in self.areas:
            if  x >= area.x and x < area.x + area.w \
                and y >= area.y and y < area.y + area.h:
                if menor_size_ctrl == None or area.size < menor_size:
                    menor_size = area.size
                    menor_size_ctrl = area.ctrl

        return menor_size_ctrl



    def on_mouse_move(self, widget, event):
        x = int( event.x )
        y = int( event.y )
        self.ctrl_over = self.get_control_at( x, y )
        self.ide.formContainer.queue_draw()
        return True



    def on_mouse_button_press(self, widget, event):
        # double click? if so, process the code add first,
        # then read its props later (so the updated information
        # about the line on which it is declared is shown)
        #
        if event.type == gtk.gdk._2BUTTON_PRESS:
            sobj = get_object_name( self.ctrl_selected )
            self.ide.analyser.code_add_for_get_object( sobj )

        x = int( event.x )
        y = int( event.y )
        
        self.ctrl_selected = self.get_control_at( x, y )
        self.ide.formContainer.queue_draw()
        self.ide.objectInspector.select_obj( self.ctrl_selected )
        return True




    def on_expose(self, widget, event):
        cr = event.window.cairo_create()
        
        cr.set_source_pixbuf( self.screenshot, 0, 0 )
        cr.paint()
        
        r1,g1,b1 = hex_to_rgb( SELECT_BORDER_COLOR1 )
        r2,g2,b2 = hex_to_rgb( SELECT_BORDER_COLOR2 )
        
        for a in self.areas:
            if a.ctrl == self.ctrl_selected:
                cr.set_dash( SELECT_BORDER_DASH_SET )
                cr.set_line_width( SELECT_BORDER_WIDTH_SET )
                offset = 0.5
                alpha = SELECT_BORDER_ALPHA_SET
            elif a.ctrl == self.ctrl_over:
                cr.set_dash( SELECT_BORDER_DASH_OVER )
                cr.set_line_width( SELECT_BORDER_WIDTH_OVER )
                offset = 0
                alpha = SELECT_BORDER_ALPHA_OVER
            else:
                continue

            grad = cairo.LinearGradient( a.x, a.y, a.x + a.w, a.y + a.h )
            grad.add_color_stop_rgba( 0.0,   r1, g1, b1, alpha )
            grad.add_color_stop_rgba( 1.0,   r2, g2, b2, alpha )

            cr.set_source( grad )
            cr.rectangle( a.x + offset, a.y + offset, a.w-1, a.h-1 )
            cr.stroke()

            coords = ( (a.x, a.y), (a.x + a.w-1, a.y), \
                (a.x + a.w-1, a.y + a.h-1), (a.x, a.y + a.h-1) )

            cr.set_dash( [] )
            cr.set_line_width( 1 )
            for coord in coords:
                x = coord[0]
                y = coord[1]

                cr.set_source_rgba( 1, 1, 1, alpha )
                cr.arc( x, y, 3, 0, 2*PI )
                cr.fill()

                cr.set_source_rgba( r1, g1, b1, alpha )
                cr.arc( x + 0.5, y + 0.5, 3, 0, 2*PI )
                cr.stroke()


        # pára aqui; nao pinta mais os controles do form.
        return True



    def draw_title_bar(self, cr, w, h):
        r1,g1,b1 = hex_to_rgb(TITLE_BAR_COLOR_TOP) 
        r2,g2,b2 = hex_to_rgb(TITLE_BAR_COLOR_BOTTOM)

        grad = cairo.LinearGradient( 0, 0, 0, h )
        grad.add_color_stop_rgb( 0.0,  r1,g1,b1 )
        grad.add_color_stop_rgb( 0.5,  r2,g2,b2 )

        cr.set_source( grad )
        cairo_rounded_rect( cr, 0, 0, w-1, h * 2 )
        cr.fill()

        cr.set_line_width( 1 )
        cr.set_source_rgb( 0, 0, 0 )
        cairo_rounded_rect( cr, 0 + 0.5, 0 + 0.5, w-1, h * 2 )
        cr.move_to( 0 + 0.5, h-1 + 0.5 )
        cr.line_to( w-1 + 0.5, h-1 + 0.5 )
        cr.stroke()

        #####

        cr.identity_matrix()
        cr.translate( TITLE_BAR_ICON_LEFT, TITLE_BAR_ICON_TOP )
        cr.set_source_pixbuf( self.img_title_bar_icon, 0, 0 )
        cr.paint()
                
        #####
        
        btn_w = self.img_title_bar_btn.get_width()
        btn_h = self.img_title_bar_btn.get_height()

        cr.identity_matrix()
        cr.translate( w - btn_w - TITLE_BAR_BTN_RIGHT, TITLE_BAR_BTN_TOP )
        cr.set_source_pixbuf( self.img_title_bar_btn, 0, 0 )
        cr.paint()

