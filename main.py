#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import vte
from itertools import groupby
from collections import OrderedDict
import os

class GshellTerm(vte.Terminal):

    def __init__(self, *args, **kwds):
        super(GshellTerm, self).__init__(*args, **kwds)
        self.fork_command()


class CloseTabButton(gtk.Button):

    def __init__(self, widget, *args, **kwds):
        super(CloseTabButton, self).__init__(label='x', *args, **kwds)
        self.set_relief(gtk.RELIEF_NONE)
        image_w, image_h = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
        self.set_size_request(image_w+7, image_h+6)
        self.widget_ref = widget
        self.connect('destroy', self.on_destroy)

    def on_destroy(self, widget):
        self.widget_ref = None


class GshellNoteBook(gtk.Notebook):

    def __init__(self, *args, **kwds):
        super(GshellNoteBook, self).__init__(*args, **kwds)
        self.set_tab_pos(gtk.POS_TOP)
        self.set_show_tabs = True
        self.set_show_border = True
        self.set_scrollable = True

    def add_tab(self, widget, title):
        tab = gtk.HBox()
        tab_label = gtk.Label("Tab")
        tab_label.show()
        tab.pack_start(tab_label)
        tab_close = CloseTabButton(widget)
        tab_close.connect('clicked', self.destroy_tab )
        tab_close.show()
        tab.pack_end( tab_close)
        tab.show()
        self.append_page(widget, tab)


    def destroy_tab(self, widget, data=None):
        page_num = self.page_num( widget.widget_ref )
        self.remove_page(page_num)
        widget.destroy()


class MainWindow(object):

    def __init__(self):
        super(MainWindow, self).__init__()

    def build_window(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(1200, 860)
        self.window.set_title("Gshell")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect("delete_event", self.main_window_destroy)
        self.terminal = GshellTerm()
        self.vbox_main = gtk.VBox()
        self.window.add(self.vbox_main)

        """ 
        Menu
        """
        self.menu = self.build_menu()
        self.vbox_main.pack_start(self.menu, False, False, 0)

        """
        ToolBar
        """
        self.toolbar = self.build_toolbar()
        self.vbox_main.pack_start(self.toolbar, False, False, 0)

        """
           Connection String
        """
        toolbar_conn = gtk.Toolbar()
        toolbar_conn.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        toolbar_conn.set_style(gtk.TOOLBAR_ICONS)
        self.conn_string = gtk.Entry()
        self.conn_string.set_size_request(350, 25)
        self.conn_string.set_editable(True)
        icon_disconnect = gtk.Image()
        icon_disconnect.set_from_stock(gtk.STOCK_CONNECT, 4)
        toolbar_conn.append_widget(self.conn_string, None, None)
        toolbar_conn.append_item("Connect", "Connect", "Connect", icon_disconnect, self.menuitem_response)
        self.vbox_main.pack_start(toolbar_conn, False, False, 0)

        """
        Notebook
        """
        self.notebook = GshellNoteBook()
        self.notebook.add_tab(self.terminal, 'Term1')
        self.vbox_main.pack_start(self.notebook, True, True, 0)

        #self.statusbar = gtk.Statusbar()
        #self.vbox_main.pack_start(self.statusbar, True, True, 0)
        self.window.show_all()

    def main_window_destroy(self, *args):
        gtk.main_quit(*args)

    def menuitem_response(self, widget, string=None):
        print 'Click menu %s' % widget

    def build_toolbar(self):
        toolbar = gtk.Toolbar()
        toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        toolbar.set_style(gtk.TOOLBAR_ICONS)

        icon_new = gtk.Image()
        icon_new.set_from_stock(gtk.STOCK_NEW, 4)
        toolbar.append_item("New", "New", "New", icon_new, self.menuitem_response)

        icon_open = gtk.Image()
        icon_open.set_from_stock(gtk.STOCK_OPEN, 4)
        toolbar.append_item("Open", "Open", "Open", icon_open, self.menuitem_response)

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_disconnect = gtk.Image()
        icon_disconnect.set_from_stock(gtk.STOCK_DISCONNECT, 4)
        toolbar.append_item("Disconnect", "Disconnect", "Disconnect", icon_disconnect, self.menuitem_response)

        icon_connect = gtk.Image()
        icon_connect.set_from_stock(gtk.STOCK_CONNECT, 4)
        toolbar.append_item("Recconnect", "Recconnect", "Recconnect", icon_connect, self.menuitem_response)

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_prop = gtk.Image()
        icon_prop.set_from_stock(gtk.STOCK_PROPERTIES, 4)
        toolbar.append_item("Properties", "Properties", "Properties", icon_prop, self.menuitem_response)

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_copy = gtk.Image()
        icon_copy.set_from_stock(gtk.STOCK_COPY, 4)
        toolbar.append_item("Copy", "Copy", "Copy", icon_copy, self.menuitem_response)

        icon_paste = gtk.Image()
        icon_paste.set_from_stock(gtk.STOCK_PASTE, 4)
        toolbar.append_item("Paste", "Paste", "Paste", icon_paste, self.menuitem_response)

        icon_find = gtk.Image()
        icon_find.set_from_stock(gtk.STOCK_FIND, 4)
        toolbar.append_item("Search", "Search", "Search", icon_find, self.menuitem_response)

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_new_group = gtk.Image()
        icon_new_group.set_from_stock(gtk.STOCK_DIRECTORY, 4)
        toolbar.append_item("New Tab Group", "New Tab Group", "New Tab Group", icon_new_group, self.menuitem_response)

        icon_arragne = gtk.Image()
        icon_arragne.set_from_stock(gtk.STOCK_ADD, 4)
        toolbar.append_item("Tab Arrange", "Tab Arrange", "Tab Arrange", icon_arragne, self.menuitem_response)

        toolbar.append_widget(gtk.SeparatorToolItem(), None, None)
        return toolbar

    def build_menu(self):
        menus = OrderedDict()
        menus['File'] = (
        {
            'name' : 'New',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 1,
            'children' : None,
        },
        {
            'name' : 'Open',
            'action' : self.menuitem_response,
            'position' : 1,
            'group' : 1,
            'children' : None,
        },
        {
            'name' : 'Save as',
            'action' : self.menuitem_response,
            'position' : 2,
            'group' : 1,
            'children' : None,
        },
        {
            'name' : 'Log',
            'action' : None,
            'position' : 0,
            'group' : 2,
            'children' : (
                {
                    'name' : 'Start',
                    'action' : self.menuitem_response,
                    'group' : 1,
                    'position' : 0,
                    'children' : None,
                },
                {
                    'name' : 'Stop',
                    'action' : self.menuitem_response,
                    'group' : 1,
                    'position' : 1,
                    'children' : None,
                },
            ) 
        },
        {
            'name' : 'Exit',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 3,
            'children' : None,
        })

        menus['Edit'] = (
        {
            'name' : 'Copy',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        { 
           'name' : 'Paste',
            'action' : self.menuitem_response,
            'position' : 1,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'Select All',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 2,
            'children' : None
        },
        {
            'name' : 'Select Screen',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 2,
            'children' : None
        })

        menus['Tab'] = (
        {
            'name' : 'New Tab',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        { 
           'name' : 'New Tab Group',
            'action' : self.menuitem_response,
            'position' : 1,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'Arrange',
            'action' : self.menuitem_response,
            'position' : 2,
            'group' : 1,
            'children' : (
                {
                    'name' : 'Arrange Vertical',
                    'action' : self.menuitem_response,
                    'group' : 1,
                    'position' : 0,
                    'children' : None,
                },
                {
                    'name' : 'Arrange Horizontal',
                    'action' : self.menuitem_response,
                    'group' : 1,
                    'position' : 1,
                    'children' : None,
                },
                {
                    'name' : 'Arrange Tiled',
                    'action' : self.menuitem_response,
                    'group' : 1,
                    'position' : 2,
                    'children' : None,
                },
                {
                    'name' : 'Merge All Tab Groups',
                    'action' : self.menuitem_response,
                    'group' : 2,
                    'position' : 0,
                    'children' : None,
                },

            )
        },
        {
            'name' : 'Close',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 2,
            'children' : None
        },
        {
            'name' : 'Close Other Tabs',
            'action' : self.menuitem_response,
            'position' : 1,
            'group' : 2,
            'children' : None
        },
        {
            'name' : 'Close All Tabs',
            'action' : self.menuitem_response,
            'position' : 2,
            'group' : 2,
            'children' : None
        },
        {
            'name' : 'Rename',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 3,
            'children' : None
        },
        {
            'name' : 'Set Color',
            'action' : self.menuitem_response,
            'position' : 3,
            'group' : 4,
            'children' : (
                {
                    'name' : 'Default',
                    'action' : self.menuitem_response,
                    'group' : 1,
                    'position' : 0,
                    'children' : None,
                },
                {
                    'name' : 'Red',
                    'action' : self.menuitem_response,
                    'group' : 2,
                    'position' : 0,
                    'children' : None,
                },
                {
                    'name' : 'Yellow',
                    'action' : self.menuitem_response,
                    'group' : 2,
                    'position' : 1,
                    'children' : None,
                },
                {
                    'name' : 'Pink',
                    'action' : self.menuitem_response,
                    'group' : 2,
                    'position' : 2,
                    'children' : None,
                },
            )
        })

        menus['Tools'] = (
        {
            'name' : 'Scripts',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'Options',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 2,
            'children' : None
        },
        )

        menus['Help'] = (
        {
            'name' : 'Help',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 1,
            'children' : None
        },
        {
            'name' : 'About',
            'action' : self.menuitem_response,
            'position' : 0,
            'group' : 2,
            'children' : None
        })

        menu_bar = gtk.MenuBar()
        for main_menu, submenus in menus.iteritems():
            main_menu_item = gtk.MenuItem(main_menu)
            menu = gtk.Menu()
            self.grouped_menu(menu, submenus)
            main_menu_item.set_submenu(menu)
            menu_bar.append(main_menu_item)
        return menu_bar

    def grouped_menu(self, parent, params):
        if type(params) == dict:
            params = [params]
        sorted_menu = sorted(params, key=lambda x:x['group'])
        menu_groups = [tuple(menus) for group, menus in groupby(sorted_menu, lambda x: x['group'])]
        for menus in menu_groups:
            for menu in sorted(menus, key=lambda x: x['position']):
                menu_item = gtk.MenuItem(menu['name'])
                if menu['action']:
                    menu_item.connect("activate", menu['action'])
                if menu['children']:
                    children_sub = gtk.Menu()
                    self.grouped_menu(children_sub, menu['children'])
                    menu_item.set_submenu(children_sub)
                parent.add(menu_item)
            if len(menu_groups) > 1 and menus != menu_groups[-1]:
                separator = gtk.SeparatorMenuItem()
                parent.add(separator)


if __name__ == '__main__':
    main_window = MainWindow()
    main_window.build_window()
    gtk.main()
