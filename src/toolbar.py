# -*- coding: utf-8 -*-

import gtk

class GshellToolbar(gtk.Toolbar):
    def __init__(self, gshell):
        super(GshellToolbar, self).__init__()
        self.gshell = gshell
        self.build_toolbar()

    def build_toolbar(self):
        self.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.set_style(gtk.TOOLBAR_ICONS)

        new_button = gtk.ToolButton(gtk.STOCK_NEW)
        new_button.connect('clicked', self.gshell.new_terminal)
        new_button.set_tooltip(gtk.Tooltips(), 'New')
        self.insert(new_button, -1)

        open_button = gtk.ToolButton(gtk.STOCK_OPEN)
        open_button.connect('clicked', self.gshell.menu_open)
        open_button.set_tooltip(gtk.Tooltips(), 'Open')
        self.insert(open_button, -1)

        self.insert(gtk.SeparatorToolItem(), -1)

        self.reconnect_button = gtk.ToolButton(gtk.STOCK_CONNECT)
        self.reconnect_button.connect('clicked', self.gshell.menu_reconnect_tab)
        self.reconnect_button.set_tooltip(gtk.Tooltips(), 'Connect')
        self.insert(self.reconnect_button, -1)

        self.disconnect_button = gtk.ToolButton(gtk.STOCK_DISCONNECT)
        self.disconnect_button.connect('clicked', self.gshell.menu_disconnect_tab)
        self.disconnect_button.set_tooltip(gtk.Tooltips(), 'Disconnect')
        self.insert(self.disconnect_button, -1)

        self.insert(gtk.SeparatorToolItem(), -1)

        self.copy_button = gtk.ToolButton(gtk.STOCK_COPY)
        self.copy_button.connect('clicked', self.gshell.menu_copy)
        self.copy_button.set_tooltip(gtk.Tooltips(), 'Copy')
        self.insert(self.copy_button, -1)

        self.paste_button = gtk.ToolButton(gtk.STOCK_PASTE)
        self.paste_button.connect('clicked', self.gshell.menu_paste)
        self.paste_button.set_tooltip(gtk.Tooltips(), 'Paste')
        self.insert(self.paste_button, -1)

        self.search_button = gtk.ToolButton(gtk.STOCK_FIND)
        self.search_button.set_tooltip(gtk.Tooltips(), "Search")
        self.search_button.connect('clicked', self.gshell.menu_search)
        self.insert(self.search_button, -1)

        self.insert(gtk.SeparatorToolItem(), -1)

        self.zoom_in_button = gtk.ToolButton(gtk.STOCK_ZOOM_IN)
        self.zoom_in_button.set_tooltip(gtk.Tooltips(), "Zoom In")
        self.zoom_in_button.connect('clicked', self.gshell.menu_zoom_tab, 'zoom_in')
        self.insert(self.zoom_in_button, -1)

        self.zoom_out_button = gtk.ToolButton(gtk.STOCK_ZOOM_OUT)
        self.zoom_out_button.set_tooltip(gtk.Tooltips(), "Zoom Out")
        self.zoom_out_button.connect('clicked', self.gshell.menu_zoom_tab, 'zoom_out')
        self.insert(self.zoom_out_button, -1)

        self.zoom_orig_button = gtk.ToolButton(gtk.STOCK_ZOOM_100)
        self.zoom_orig_button.set_tooltip(gtk.Tooltips(), "Zoom Default")
        self.zoom_orig_button.connect('clicked', self.gshell.menu_zoom_tab, 'zoom_orig')
        self.insert(self.zoom_orig_button, -1)

        self.insert(gtk.SeparatorToolItem(), -1)
