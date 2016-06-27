# -*- coding: utf-8 -*-

import gtk

class GshellToolbar(gtk.Toolbar):
    def __init__(self, main_window):
        super(GshellToolbar, self).__init__()
        self.main_window = main_window
        self.build_toolbar()

    def build_toolbar(self):
        self.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.set_style(gtk.TOOLBAR_ICONS)

        icon_new = gtk.Image()
        icon_new.set_from_stock(gtk.STOCK_NEW, 4)
        self.append_item("New", "New", "New", icon_new, self.main_window.new_terminal)

        icon_open = gtk.Image()
        icon_open.set_from_stock(gtk.STOCK_OPEN, 4)
        self.append_item("Open", "Open", "Open", icon_open, self.main_window.menu_open)

        self.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_reconnect = gtk.Image()
        icon_reconnect.set_from_stock(gtk.STOCK_CONNECT, 4)
        self.append_item("Reconnect", "Reconnect", "Reconnect", icon_reconnect, self.main_window.menu_reconnect_tab)

        icon_disconnect = gtk.Image()
        icon_disconnect.set_from_stock(gtk.STOCK_DISCONNECT, 4)
        self.append_item("Disconnect", "Disconnect", "Disconnect", icon_disconnect, self.main_window.menu_disconnect_tab)

        self.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_prop = gtk.Image()
        icon_prop.set_from_stock(gtk.STOCK_PROPERTIES, 4)
        self.append_item("Properties", "Properties", "Properties", icon_prop, self.main_window.menuitem_response)

        self.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_copy = gtk.Image()
        icon_copy.set_from_stock(gtk.STOCK_COPY, 4)
        self.append_item("Copy", "Copy", "Copy", icon_copy, self.main_window.menu_copy)

        icon_paste = gtk.Image()
        icon_paste.set_from_stock(gtk.STOCK_PASTE, 4)
        self.append_item("Paste", "Paste", "Paste", icon_paste, self.main_window.menu_paste)

        icon_find = gtk.Image()
        icon_find.set_from_stock(gtk.STOCK_FIND, 4)
        self.append_item("Search", "Search", "Search", icon_find, self.main_window.menuitem_response)

        self.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_zoom_in = gtk.Image()
        icon_zoom_in.set_from_stock(gtk.STOCK_ZOOM_IN, 4)
        self.append_item("Zoom In", "Zoom In", "Zoom In", icon_zoom_in, self.main_window.menu_zoom_tab, 'zoom_in')

        icon_zoom_out = gtk.Image()
        icon_zoom_out.set_from_stock(gtk.STOCK_ZOOM_OUT, 4)
        self.append_item("Zoom Out", "Zoom Out", "Zoom Out", icon_zoom_out, self.main_window.menu_zoom_tab, 'zoom_out')

        icon_zoom_orig = gtk.Image()
        icon_zoom_orig.set_from_stock(gtk.STOCK_ZOOM_100, 4)
        self.append_item("Zoom Default", "Zoom Default", "Zoom Default", icon_zoom_orig, self.main_window.menu_zoom_tab, 'zoom_orig')

        self.append_widget(gtk.SeparatorToolItem(), None, None)

        icon_new_group = gtk.Image()
        icon_new_group.set_from_stock(gtk.STOCK_DIRECTORY, 4)
        self.append_item("New Tab Group", "New Tab Group", "New Tab Group", icon_new_group, self.main_window.menuitem_response)

        icon_arragne = gtk.Image()
        icon_arragne.set_from_stock(gtk.STOCK_ADD, 4)
        self.append_item("Tab Arrange", "Tab Arrange", "Tab Arrange", icon_arragne, self.main_window.menuitem_response)

        self.append_widget(gtk.SeparatorToolItem(), None, None)
