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

        self.captured_gui = None
        self.captured_gui_ok = False
        self.main_window = None
        self.main_w = 0
        self.main_h = 0
        self.areas = []

        self.ide = ide



    def load_from_file(self, glade_filename):

        builder = gtk.Builder()
        builder.add_from_file( glade_filename )

        self.formControls = FormControls()
        self.formControls.objs = builder.get_objects()

        for obj in self.formControls.objs:
            try:
                obj_name = obj.get_name()
            except:
                obj_name = obj.__class__.__name__ + "_" + str(hash(obj))

            setattr( self.formControls, obj_name, obj )

            if isinstance( obj, gtk.Window ):
                self.main_window = obj


        if self.main_window == None:
            print("*** No window found in the glade file!")
            return


        # define a aparencia do form
        #
        self.ide.formTitle.set_text( self.main_window.get_title() )
        w, h = self.main_window.get_size()
        h += self.ide.formTitleBar.get_size_request()[1]
        self.ide.formFrame.set_size_request( w, h )



        child = self.main_window.get_child()
        self.main_window.remove( child )
        self.ide.formContainer.add( child )

        # na verdade, vamos usar o child do main_window, pois a window em
        # si eh somente o child junto com um decorator do window manager.
        #
        self.main_window = child

        self.ide.formBox.connect( "motion-notify-event", self.on_mouse_move )
        self.ide.formBox.connect( "button-press-event", self.on_mouse_button_press )
        self.ide.formContainer.connect( "expose-event", self.on_expose )

        # temos que mostrar a janela mesmo, de um jeito ou de outro,
        # pois o gtk usa necessariamente o backend (x11 por ex.) pra
        # desenhar os widgets. uma nova versao (client-side-windows, csw)
        # permite desenhar tudo direto no gdk, sem backends. isso podera
        # ser usado para incorporar texturas, composite, clutter, etc.
        #
        self.main_window.show()

        # deixa aparecer na tela com tudo
        while gtk.events_pending():
            gtk.main_iteration( block=False )

        # tira uma foto
        self.screenshot()

        # processa o que ainda tem que processar
        while gtk.events_pending():
            gtk.main_iteration( block=False )

        # por fim, tira da tela
        self.main_window.hide()




    def screenshot(self):

        # supoe que os allocations ja foram feitos.

        self.captured_gui = None
        self.captured_gui_ok = False

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

        self.main_w = self.main_window.get_allocation().width
        self.main_h = self.main_window.get_allocation().height

        # isso força um expose
        drawable = self.main_window.get_snapshot( None )

        while gtk.events_pending():
            gtk.main_iteration( block=False )

        self.captured_gui = gtk.gdk.Pixbuf( gtk.gdk.COLORSPACE_RGB,
            False, 8, self.main_w, self.main_h )
        self.captured_gui.get_from_drawable( drawable, \
            gtk.gdk.colormap_get_system(), 0, 0, 0, 0, self.main_w, self.main_h )
        self.captured_gui_ok = True




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

            sobj = self.ctrl_selected.get_name()
            self.ide.analyser.code_add_for_get_object( sobj )


        x = int( event.x )
        y = int( event.y )

        self.ctrl_selected = self.get_control_at( x, y )
        self.ide.formContainer.queue_draw()
        self.ide.objectInspector.select_obj( self.ctrl_selected )

        return True



    def on_expose(self, widget, event):

        if not self.captured_gui_ok:
            return False

        else:
            cr = event.window.cairo_create()

            cr.set_source_rgb(1, 1, 1)
            cr.paint()

            cr.set_source_pixbuf( self.captured_gui, 0, 0 )
            cr.paint()

            for a in self.areas:

                if a.ctrl == self.ctrl_selected:
                    cr.set_dash( [] )
                    cr.set_line_width( 3 )
                    alpha = 1
                elif a.ctrl == self.ctrl_over:
                    cr.set_dash( [3] )
                    cr.set_line_width( 2 )
                    alpha = 0.5
                else:
                    continue

                grad = cairo.LinearGradient( a.x, a.y, a.x + a.w, a.y + a.h )
                grad.add_color_stop_rgba( 0.0,   0.4, 0.4, 0.9, alpha )
                grad.add_color_stop_rgba( 1.0,   0.2, 0.8, 0.9, alpha )

                cr.set_source( grad )
                cr.rectangle( a.x + 0.5, a.y + 0.5, a.w-1, a.h-1 )
                cr.stroke()

                coords = ( (a.x, a.y), (a.x + a.w-1, a.y), \
                    (a.x + a.w-1, a.y + a.h-1), (a.x, a.y + a.h-1) )

                cr.set_dash( [] )
                cr.set_line_width( 1 )
                for coord in coords:
                    x = coord[0]
                    y = coord[1]

                    cr.set_source_rgba( 1, 1, 1, alpha )
                    cr.arc( x, y, 3, 0, 2 * 3.14159265 )
                    cr.fill()

                    cr.set_source_rgba( 0.2, 0.4, 1, alpha )
                    cr.arc( x + 0.5, y + 0.5, 3, 0, 2 * 3.14159265 )
                    cr.stroke()


            # pára aqui; nao pinta mais os controles do form.
            return True
