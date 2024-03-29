#!/usr/bin/env python
#-*- coding:utf-8 -*-

import gtk
import cairo
import pango
import os

from utils import *
from ideForm import *
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
        self.labInvalidObjects = builder.get_object("labInvalidObjects")        
        self.checkContainers = builder.get_object( "checkContainers" )

        self.textInfo.modify_base( gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffbd") )
        self.textInfo.modify_font( pango.FontDescription("8") )
        #self.formView.modify_bg( gtk.STATE_NORMAL, gtk.gdk.color_parse("white") )
        self.formView.modify_bg( gtk.STATE_NORMAL, gtk.gdk.color_parse("#7b7878") )
        
        self.formTitleBar.set_app_paintable( True )
        self.formTitleBar.modify_bg( gtk.STATE_NORMAL, gtk.gdk.color_parse("#7b7878") )

        self.objectInspector = ObjectInspector( self )
        self.form = Form( self )
        self.analyser = None
        self.glade_file = None

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
        self.labInvalidObjects.connect( "activate-link", self.on_labInvalidObjects_activate_link )
        self.checkContainers.connect( "toggled",        self.on_checkContainers_toggled )




    def run(self, glade_file = None, parentWindow = None, analyser = None):
        self.analyser = analyser
        self.glade_file = glade_file

        self.window.show()

        if self.glade_file != None:
            self.form.load_from_file( glade_file )
            if self.analyser != None:
                self.check_for_objects_declared()
        
        self.objectInspector.read_callbacks()

        self.parentWindow = parentWindow
        if self.parentWindow:
            self.window.set_transient_for( parentWindow )
        else:
            gtk.main()


    def on_close(self, *args):
        if hasattr(self, 'parentWindow') and self.parentWindow != None:
            self.window.hide()
            return True
        else:
            gtk.main_quit()
            return False


    def on_draw_titlebar(self, sender, event):
        cr = event.window.cairo_create()
        w = self.formTitle.get_allocation().width
        h = self.formTitle.get_allocation().height

        self.form.draw_title_bar( cr, w, h )
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
        self.form.ctrl_over = None
        self.formContainer.queue_draw()        
        self.objectInspector.select_obj( obj, select_item_in_list=False )




    def on_implement_signal(self, *args):
        path, col = self.listSignals.get_cursor()
        if path == None:
            return
        
        it = self.storeSignals.get_iter( path )

        obj_name = get_object_name( self.objectInspector.selected_obj )
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

        while gtk.events_pending(): gtk.main_iteration( block=False )

        self.analyser.view.place_cursor_onscreen()
        self.analyser.view.grab_focus()

        while gtk.events_pending(): gtk.main_iteration( block=False )
        
        self.renova()



    def renova(self):
        self.objectInspector.select_obj( self.objectInspector.selected_obj )
        self.objectInspector.read_callbacks()

        self.analyser.re_inspect()
        self.check_for_objects_declared()


    def check_for_objects_declared(self):
        # checks if all declared objects in the code [self.xx = builder.get_object('xx')]
        # are indeed declared in the glade file.
        #
        not_found = []
        
        objs = self.analyser.list_for_get_object # [obj, line]
        for sobj, line_num in objs:
            
            found_in_glade = False

            #for obj_info in self.storeObjects:
            #    if obj_info[3] == sobj:
            for obj in self.form.formControls.objs:
                if get_object_name( obj ) == sobj:
                    
                    found_in_glade = True
                    break
            
            if not found_in_glade:
                not_found.append( [sobj, line_num] )
        
        self.labInvalidObjects.set_visible( len(not_found) > 0 )
        self.labInvalidObjects.set_data( "easy-gui-code-invalid-objects", not_found )

            

    def on_labInvalidObjects_activate_link(self, *args):
        self.labInvalidObjects.hide()
        not_found = self.labInvalidObjects.get_data( "easy-gui-code-invalid-objects" )

        lines_to_remove = [ line_num for sobj, line_num in not_found ]
        lines_to_remove.sort( reverse=True )
        
        for line_to_remove in lines_to_remove:
            print "Removing line %d..." % (line_to_remove+1)
        
        self.analyser.code_remove( lines_to_remove )
                    
        self.renova()        
        return True
    


    def on_access_activate_link(self, *args):
        obj_name = get_object_name( self.objectInspector.selected_obj )
        self.analyser.code_add_for_get_object( obj_name )
        
        self.renova()
        return True


    def on_checkContainers_toggled(self, widget):
        self.form.read_objects()


    def on_open_glade(self, sender):
        if self.glade_file:
            os.system( "glade \"%s\" &" % self.glade_file )
            self.on_close()
        else:
            alert( "No glade file!", "Open Glade file" )


if __name__ == '__main__':
    IDE().run( glade_file = "newCode.glade" )

