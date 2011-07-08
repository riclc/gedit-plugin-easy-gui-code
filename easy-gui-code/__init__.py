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


import gedit
import gtk
import gio
import os

from utils import *
from docAnalyser import DocAnalyser
from newCode import *
from ide import IDE


ui = """
<ui>
    <menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_2">
        <menuitem action="OpenGuiFile" />
      </placeholder>
    </menu>
    </menubar>

    <toolbar name="ToolBar">
        <separator/>
        <toolitem action="OpenGuiFile"/>
    </toolbar>
</ui>
"""



class EasyGuiCodePlugin(gedit.Plugin):
    def __init__(self):
        gedit.Plugin.__init__(self)

        self.action_group = None
        self.ui_id = None
        self.window = None

        self.analyser = DocAnalyser()


    def activate(self, window):
        self.window = window
        self.action_group = gtk.ActionGroup('EasyGuiCodePluginActions')
        self.action_group.add_actions([(
            'OpenGuiFile',
            gtk.STOCK_PAGE_SETUP,
            'Open _GUI file...',
            None,
            'Opens the GtkBuilder .glade file being used in the code',
            self.on_open_gui_file_activate
        )])

        uim = window.get_ui_manager()
        uim.insert_action_group(self.action_group, -1)
        self.ui_id = uim.add_ui_from_string( ui )


    def deactivate(self, window):
        uim = window.get_ui_manager()
        uim.remove_ui(self.ui_id)
        uim.remove_action_group(self.action_group)
        uim.ensure_update()

        self.action_group = None
        self.ui_id = None
        self.window = None


    def on_open_gui_file_activate(self, *args):
        doc = self.window.get_active_document()
        view = self.window.get_active_view()
        self.analyser.inspect( doc, view )

        doc_file = doc.get_uri()
        if doc_file == None:
            NewCode().run( parentWindow = self.window, doc = doc )
            return

        doc_file = gio.File( doc_file ).get_path()
        doc_dir = os.path.dirname( doc_file )

        if self.analyser.builder_file == None:
            NewCode().run( parentWindow = self.window, doc = doc, dir_path = doc_dir )
            return

        glade_file = os.path.join( doc_dir, self.analyser.builder_file )
        if os.path.exists( glade_file ):
            IDE().run( \
                glade_file = glade_file, \
                parentWindow = self.window, \
                analyser = self.analyser )

        else:
            alert( "Glade file being used <b>%s</b> was not found!" % glade_file, \
                "Open GUI file" )


    def update_ui(self, window):
        doc = self.window.get_active_document()
        self.action_group.set_sensitive(doc is not None)

