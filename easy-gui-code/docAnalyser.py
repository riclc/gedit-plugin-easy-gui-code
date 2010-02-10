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



class DocAnalyser:


    def reset(self):
        self.find_string_caret = 0

        self.var_builder = None
        self.builder_file = None

        self.last_line_for_get_object = None
        self.last_line_for_connect = None
        self.last_line_for_proc = None

        self.list_for_get_object = [] # [obj, line]
        self.list_for_connect = [] # [obj, event, callback, line]
        self.list_for_proc = [] # [proc, line]



    def __init__(self):
        self.doc = None
        self.view = None
        self.reset()


    def re_inspect(self):
        self.inspect( self.doc, self.view )


    def inspect(self, doc, view):
        self.doc = doc
        self.view = view

        self.reset()

        bounds = self.doc.get_bounds()
        lines = range( bounds[0].get_line(), bounds[1].get_line()+1 )


        pre_line = ""

        for i in lines:
            line_start = self.doc.get_iter_at_line( i )

            # without this, empty lines will make for repeated lines
            if line_start.ends_line():
                continue

            line_end = line_start.copy()
            line_end.forward_to_line_end()

            line_text = self.doc.get_text( line_start, line_end ).strip()

            if line_text[-1:] == '\\':
                pre_line = line_text[:-1]
            elif pre_line:
                line_text = pre_line + line_text
                pre_line = ""

            if not pre_line:
                self.inspect_line( line_text, i )




    def find_string(self, lin):

        p1 = lin.find( "\"" )
        p2 = lin.find( "\'" )

        if p1 != -1 and p2 == -1:
            pos = p1
            ch = "\""
        elif p1 == -1 and p2 != -1:
            pos = p2
            ch = "\'"
        elif p1 != -1 and p2 != -1:
            if p1 < p2:
                pos = p1
                ch = "\""
            else:
                pos = p2
                ch = "\'"
        else:
            pos = -1

        if pos != -1:
            pos_end = lin.find( ch, pos+1 )

            if pos_end != -1:
                self.find_string_caret = pos_end+1
                return lin[ pos+1:pos_end ]

        return None






    def try_var_builder(self, lin):

        pos = lin.find( "gtk.Builder(" )

        if pos != -1:
            pos = lin.find( "=" )
            if pos != -1:
                self.var_builder = lin[: pos].strip()
                return True

        return False




    def try_builder_file(self, lin):

        pos = lin.find( "add_from_file" )

        if pos != -1:
            pos += len( "add_from_file" )

            if self.var_builder in lin:
                lin = lin[ pos: ]
                pos = lin.find( "(" )

                if pos != -1:
                    self.builder_file = self.find_string( lin )
                    return True

        return False




    def try_get_object(self, lin, lin_num):

        s_get_object = self.var_builder + ".get_object("
        pos = lin.find( s_get_object )

        if pos != -1:
            pos += len( s_get_object )
            lin = lin[ pos: ]

            sobj = self.find_string( lin )
            self.list_for_get_object.append( [sobj, lin_num] )

            self.last_line_for_get_object = lin_num
            return True

        return False




    def try_proc(self, lin, lin_num):

        lin = lin.strip()

        if lin[:4] == 'def ':

            p = lin.find( "(", 4 )
            if p != -1:

                sproc = lin[4:p].strip()
                self.list_for_proc.append( [sproc, lin_num] )
                self.last_line_for_proc = lin_num
                return True


        return False




    def try_connect(self, lin, lin_num):

        s_connect = ".connect("
        pos = lin.find( s_connect )

        if pos == -1:
            # tenta com connect_after
            s_connect = ".connect_after("
            pos = lin.find( s_connect )
            
        if pos != -1:
            s_self = "self."
            pos_self = lin.find( s_self )

            if pos_self != -1:
                sobj = lin[ pos_self + len(s_self) : pos ]

                lin = lin[ pos + len(s_connect) + 1 : ]
                sevent = self.find_string( lin )

                pos_self = lin.find( s_self )
                if pos_self != -1:

                    lin = lin[ pos_self + len(s_self): ]
                    pos = lin.find( ")" )

                    if pos != -1:
                        scallback = lin[: pos].strip()

                        info = [sobj, sevent, scallback, lin_num]
                        self.list_for_connect.append( info )
                        self.last_line_for_connect = lin_num
                        return True

        return False




    def inspect_line(self, lin, lin_num ):

        if self.var_builder == None:
            self.try_var_builder( lin )

        elif self.builder_file == None:
            self.try_builder_file( lin )

        else:
            if self.try_get_object( lin, lin_num ):
                return

            if self.try_proc( lin, lin_num ):
                return

            if self.try_connect( lin, lin_num ):
                return




    def code_add(self, code, insert_at_line = -1, re_inspect = True):

        if insert_at_line == -1:
            it = self.doc.get_end_iter()
        else:
            it = self.doc.get_iter_at_line( insert_at_line )

        self.doc.insert( it, code )


        while gtk.events_pending():
            gtk.main_iteration( block=False )


        if insert_at_line == -1:
            it = self.doc.get_end_iter()
        else:
            it = self.doc.get_iter_at_line( insert_at_line )

        self.view.scroll_to_iter( it, within_margin = 0.05, \
            use_align = True, xalign = 0.0, yalign = 1.0 )

        if re_inspect:
            self.re_inspect()



    def code_add_to_current_line(self, code):

        self.doc.insert_at_cursor( code + "\n" )

        while gtk.events_pending():
            gtk.main_iteration( block=False )




    def code_add_for_get_object(self, sobj, re_inspect = True):

        for obj, lin in self.list_for_get_object:
            if obj == sobj:
                return # do not add the same object again

        code = "        self.%s = %s.get_object( \"%s\" )\n" % \
                (sobj, self.var_builder, sobj)

        line_num = self.last_line_for_get_object+1

        self.code_add( code, line_num, re_inspect )



    def code_add_for_event(self, sobj, sevent, scallback, scallback_decl, callback_after):

        # for each code_add, we must re-inspect the code, because the
        # self.last_line_for_xxxx's must be updated.
        #

        self.code_add_for_get_object( sobj )

        if callback_after:
            connect_cmd = "connect_after"
        else:
            connect_cmd = "connect"

        self.code_add( \
            "        self.%s.%s( \"%s\", %s )\n" % \
            (sobj, connect_cmd, sevent, "self." + scallback), \
            self.last_line_for_connect+1 )


        if scallback_decl != None:
            self.code_add( "\n" + scallback_decl + "\n\n", \
                self.last_line_for_proc-1 )



    def code_goto(self, line):

        it = self.doc.get_iter_at_line( line )
        self.view.scroll_to_iter( it, within_margin = 0.05, \
            use_align = True, xalign = 0.0, yalign = 1.0 )




    def check_obj_signal(self, obj_name, signal_name):

        for connect in self.list_for_connect:
            if connect[0] == obj_name and connect[1] == signal_name:
                return True, connect[3]

        return False, -1
