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
import gtksourceview2

import sys
sys.path.append( \
    os.path.abspath( \
        os.path.join( \
            os.path.dirname(__file__),
            ".." \
        ) \
    ) \
)
from utils import *


glade_src = """<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <requires lib="gtk+" version="2.24"/>
  <!-- interface-naming-policy project-wide -->
  <object class="GtkWindow" id="window1">
    <property name="can_focus">False</property>
    <property name="window_position">center</property>
    <property name="default_width">200</property>
    <property name="default_height">150</property>
    <child>
      <object class="GtkVBox" id="vbox1">
        <property name="visible">True</property>
        <property name="can_focus">False</property>
        <property name="border_width">4</property>
        <property name="spacing">2</property>
        <child>
          <placeholder/>
        </child>
        <child>
          <object class="GtkHBox" id="hbox1">
            <property name="visible">True</property>
            <property name="can_focus">False</property>
            <property name="spacing">2</property>
            <child>
              <placeholder/>
            </child>
            <child>
              <placeholder/>
            </child>
            <child>
              <placeholder/>
            </child>
          </object>
          <packing>
            <property name="expand">True</property>
            <property name="fill">True</property>
            <property name="position">1</property>
          </packing>
        </child>
        <child>
          <placeholder/>
        </child>
      </object>
    </child>
  </object>
</interface>
"""


class NewCode:
    def __init__(self):
        mydir = os.path.dirname(__file__)
        builder = gtk.Builder()
        builder.add_from_file( os.path.join( mydir, "newCode.glade" ) )
        
        self.window1 = builder.get_object( "window1" )
        self.btnOK = builder.get_object( "btnOK" )
        self.btnCancel = builder.get_object( "btnCancel" )
        self.btnNew = builder.get_object( "btnNew" )
        self.btnFind = builder.get_object("btnFind")
        self.entryPath = builder.get_object("entryPath")        

        self.window1.connect( "delete-event", self.on_close )
        self.btnCancel.connect( "clicked", self.on_close )
        self.btnOK.connect( "clicked", self.on_ok )
        self.btnNew.connect( "clicked", self.on_btnNew_clicked )
        self.btnFind.connect( "clicked", self.on_btnFind_clicked )
        self.window1.connect( "map", self.on_window_start )


    def run(self, parentWindow = None, dir_path = None, doc = None):
        self.doc = doc
        if dir_path != None:
            self.entryPath.set_text( dir_path + os.path.sep )

        self.window1.show()
        self.parentWindow = parentWindow
        if self.parentWindow:
            self.window1.set_transient_for( parentWindow )
        else:
            gtk.main()


    def on_window_start(self, window):
        h = 180
        self.window1.window.set_geometry_hints( \
            min_width=400, max_width=1000, \
            min_height=h, max_height=h )


    def on_close(self, *args):
        if self.parentWindow:
            self.window1.hide()
            return True
        else:
            gtk.main_quit()
            return False


    def on_btnFind_clicked(self, widget):
        dir_path = os.path.dirname( self.entryPath.get_text() )
        filename = open_dialog( "Glade (*.glade)", self.window1, dir_path )
        if filename != None:
            self.entryPath.set_text( filename )
    
    
    def on_btnNew_clicked(self, widget):
        dir_path = os.path.dirname( self.entryPath.get_text() )
        filename = save_dialog( "Glade (*.glade)", self.window1, dir_path )
        if filename != None:
            f = open( filename, "w" )
            f.write( glade_src )
            f.close()
            
            self.entryPath.set_text( filename )


    def on_ok(self, *args):
        filename = self.entryPath.get_text()
        if self.doc and os.path.isfile( filename ):
            self.gen_code( self.doc, filename )
        self.on_close()
    

    def gen_code(self, doc, glade_file ):
        objs = get_objects_with_names_from_glade_file( glade_file )

        code_objs = ""
        main_window = ""

        for obj in objs:
            if not is_basic_object( obj ) or is_container_object( obj ):
                continue

            try:
                obj_name = get_object_name( obj )
            except:
                continue

            code_objs += "        self.%s = builder.get_object( \"%s\" )\n" % \
                (obj_name, obj_name)

            if isinstance( obj, gtk.Window ):
                main_window = obj_name

        if main_window == "":
            print("*** No window found in the glade file!")
            main_window = "window"

        code_class = os.path.splitext( os.path.basename( glade_file ) )[0].capitalize()
        glade_file_basename = os.path.basename( glade_file )

        code1 = """#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import gtk
import pango


class %s:
    def __init__(self):
        self.my_dir = os.path.dirname(__file__)
        builder = gtk.Builder()
        builder.add_from_file( os.path.join( self.my_dir, \"%s\" ) )
        
%s
"""     % (code_class, glade_file_basename, code_objs)


        code2 = """
        self.%s.connect( \"delete-event\", self.on_close )

"""     % (main_window)


        code3 = """
    def run(self, parent_window = None):
        self.%s.show()
        self.parent_window = parent_window
        if self.parent_window:
            self.%s.set_transient_for( parent_window )
        else:
            gtk.main()


    def on_close(self, *args):
        if self.parent_window:
            self.%s.hide()
            return True
        else:
            gtk.main_quit()
            return False


if __name__ == '__main__':
    %s().run()
"""     % (main_window, main_window, main_window, code_class)

        code = code1 + code2 + code3

        it = doc.get_start_iter()
        doc.insert( it, code )
        while gtk.events_pending(): gtk.main_iteration( block=False )

        lang_python = gtksourceview2.language_manager_get_default().get_language("python")
        doc.set_language( lang_python )



if __name__ == '__main__':
    NewCode().run()

