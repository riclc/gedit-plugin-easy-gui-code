#!/usr/bin/env python
#-*- coding:utf-8 -*-

import gtk
import cairo
import pango
import os
import os.path

from msgbox import alert
from images import Images, ObjectImages
from ideForm import Form
from ideFormTitleBar import draw_titlebar
from ideObjectInspector import ObjectInspector


class IDE:

    def __init__(self):

        mydir = os.path.dirname(__file__) 
        builder = gtk.Builder()
        builder.add_from_file( os.path.join( mydir, "ide.glade" ) )

        self.window = builder.get_object( "window" )
        self.textInfo = builder.get_object( "textInfo" )
        self.imgObject = builder.get_object( "imgObject" )
        self.labObject = builder.get_object( "labObject" )
        self.formView = builder.get_object( "formView" )
        self.formContainer = builder.get_object( "formContainer" )
        self.formFrame = builder.get_object( "formFrame" )
        self.formBox = builder.get_object( "formBox" )
        self.formTitle = builder.get_object( "formTitle" )
        self.formTitleBar = builder.get_object( "formTitleBar" )
        self.listProps = builder.get_object( "listProps" )
        self.storeProps = builder.get_object( "storeProps" )
        self.listSignals = builder.get_object( "listSignals" )
        self.storeSignals = builder.get_object( "storeSignals" )
        self.labAccess = builder.get_object( "labAccess" )
        self.btnOpenGlade = builder.get_object( "btnOpenGlade" )
        self.btnImplementSignal = builder.get_object( "btnImplementSignal" )
        self.listObjects = builder.get_object( "listObjects" )
        self.storeObjects = builder.get_object( "storeObjects" )
        self.checkConnectAfter = builder.get_object("checkConnectAfter")
        self.comboCallbacks = builder.get_object( "comboCallbacks" )
        self.storeCallbacks = builder.get_object( "storeCallbacks" )

        self.textInfo.modify_base( gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffbd") )
        self.textInfo.modify_font( pango.FontDescription("8") )
        self.formView.modify_bg( gtk.STATE_NORMAL, gtk.gdk.color_parse("white") )

        self.images = Images()
        self.objectImages = ObjectImages()
        self.objectInspector = ObjectInspector( self )
        self.form = Form( self )
        self.analyser = None
        self.glade_file = None

        self.formTitleBar.set_app_paintable( True )
        self.titleBarClose = self.images.by_name( "close" )

        self.formTitleBar.connect( "expose-event",      self.on_draw_titlebar )
        self.formBox.connect_after( "expose-event",     self.on_draw_border )
        self.window.connect( "delete-event",            self.on_close )
        self.btnOpenGlade.connect( "clicked",           self.on_open_glade )
        self.btnImplementSignal.connect( "clicked",     self.on_implement_signal )
        self.labAccess.connect( "activate-link",        self.on_access_activate_link )
        self.listObjects.connect( "cursor-changed",     self.on_list_objects_select )

        self.listProps.connect( "cursor-changed",       self.objectInspector.on_select_prop )
        self.listSignals.connect( "cursor-changed",     self.objectInspector.on_select_signal )
        self.listProps.connect( "row-activated",        self.objectInspector.on_exec_prop )
        self.listSignals.connect( "row-activated",      self.on_implement_signal )




    def run(self, glade_file = None, parentWindow = None, \
            analyser = None):

        self.analyser = analyser
        self.glade_file = glade_file

        self.window.show()

        if self.glade_file:
            self.form.load_from_file( glade_file )
        
        self.objectInspector.read_callbacks()

        self.parentWindow = parentWindow
        if self.parentWindow:
            self.window.set_transient_for( parentWindow )
        else:
            gtk.main()


    def on_close(self, *args):

        if self.parentWindow:
            self.window.hide()
            return True
        else:
            gtk.main_quit()
            return False


    def on_draw_titlebar(self, sender, event):

        cr = event.window.cairo_create()
        w = self.formTitle.get_allocation().width
        h = self.formTitle.get_allocation().height

        draw_titlebar( cr, w, h, self.titleBarClose )
        return False


    def on_draw_border(self, sender, event):

        cr = event.window.cairo_create()
        w = self.formBox.get_allocation().width
        h = self.formBox.get_allocation().height

        cr.set_line_width( 1 )
        cr.set_source_rgba( 0, 0, 0, 1 )
        cr.rectangle( 0 + 0.5, -1 + 0.5, w-1, h )
        cr.stroke()

        return True


    def on_list_objects_select(self, *args):
        
        path, col = self.listObjects.get_cursor()
        if path == None:
            return

        it = self.storeObjects.get_iter( path )
        obj = self.storeObjects.get_value( it, 2 )
        
        self.form.ctrl_selected = obj 
        self.formContainer.queue_draw()        
        self.objectInspector.select_obj( obj )




    def on_implement_signal(self, *args):

        path, col = self.listSignals.get_cursor()
        if path == None:
            return
        
        it = self.storeSignals.get_iter( path )

        obj_name = self.objectInspector.selected_obj.get_name()
        event_name = self.storeSignals.get_value( it, 1 )
        
        # podemos usar um callback existente ou criar um novo
        i = self.comboCallbacks.get_active()
        if i == -1 or i == 0:
            callback_name = self.objectInspector.signal_callback( it, True )
            callback_decl = self.objectInspector.signal_callback_full( it, indent = "    " )
        else:
            callback_name = self.storeCallbacks[i][1]
            callback_decl = None
        
        
        # podemos usar connect() ou connect_after(). depois de fazer isso,
        # volta pro estado default, que é connect() simplesmente.
        callback_after = self.checkConnectAfter.get_active()
        self.checkConnectAfter.set_active( False )        

        sig_implemented, sig_line = self.analyser.check_obj_signal( \
            obj_name, event_name )
        if sig_implemented:
            print "Signal already implemented: %s.%s" % (obj_name, event_name)
            return

        self.analyser.code_add_for_event( obj_name, event_name, \
            callback_name, callback_decl, callback_after )

        #self.on_close()

        while gtk.events_pending():
            gtk.main_iteration( block=False )

        self.analyser.view.place_cursor_onscreen()
        self.analyser.view.grab_focus()

        while gtk.events_pending():
            gtk.main_iteration( block=False )
        
        
        self.renova()



    def renova(self):
        
        #self.analyser.re_inspect()
        self.objectInspector.select_obj( self.objectInspector.selected_obj )
        self.objectInspector.read_callbacks()



    def on_access_activate_link(self, *args):

        obj_name = self.objectInspector.selected_obj.get_name()
        self.analyser.code_add_for_get_object( obj_name )
        #self.on_close()
        
        self.renova()



    def on_open_glade(self, sender):

        if self.glade_file:
            os.system( "glade-3 %s &" % self.glade_file )
            self.on_close()
        else:
            alert( "No glade file!", "Open Glade file" )


if __name__ == '__main__':
    IDE().run( glade_file = "newCode.glade" )
