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

        icon_new = gtk.Image()
        icon_new.set_from_stock(gtk.STOCK_NEW, 4)
        self.append_item("New", "New", "New", icon_new, self.gshell.new_terminal)

        icon_open = gtk.Image()
        icon_open.set_from_stock(gtk.STOCK_OPEN, 4)
        self.append_item("Open", "Open", "Open", icon_open, self.gshell.menu_open)

        self.append_widget(gtk.SeparatorToolItem(), None, None)

        self.reconnect_button = gtk.ToolButton(gtk.STOCK_CONNECT)
        self.reconnect_button.set_label("Reconnect")
        self.reconnect_button.set_sensitive(False)
        self.reconnect_button.connect('clicked', self.gshell.menu_reconnect_tab)
        self.append_widget(self.reconnect_button, "Reconnect", "Reconnect")

        self.disconnect_button = gtk.ToolButton(gtk.STOCK_DISCONNECT)
        self.disconnect_button.set_label("Disconnect")
        self.disconnect_button.set_sensitive(False)
        self.disconnect_button.connect('clicked', self.gshell.menu_disconnect_tab)
        self.append_widget(self.disconnect_button, "Disconnect", "Disconnect")

        self.append_widget(gtk.SeparatorToolItem(), None, None)

        self.properies_button = gtk.ToolButton(gtk.STOCK_PROPERTIES)
        self.properies_button.set_label("Properties")
        self.properies_button.set_sensitive(False)
        self.properies_button.connect('clicked', self.gshell.menuitem_response)
        self.append_widget(self.properies_button, "Properties", "Properties")

        self.append_widget(gtk.SeparatorToolItem(), None, None)

        self.copy_button = gtk.ToolButton(gtk.STOCK_COPY)
        self.copy_button.set_label("Copy")
        self.copy_button.set_sensitive(False)
        self.copy_button.connect('clicked', self.gshell.menu_copy)
        self.append_widget(self.copy_button, "Copy", "Copy")

        self.paste_button = gtk.ToolButton(gtk.STOCK_PASTE)
        self.paste_button.set_label("Paste")
        self.paste_button.set_sensitive(False)
        self.paste_button.connect('clicked', self.gshell.menu_paste)
        self.append_widget(self.paste_button, "Paste", "Paste")

        self.search_button = gtk.ToolButton(gtk.STOCK_FIND)
        self.search_button.set_label("Search")
        self.search_button.set_sensitive(False)
        self.search_button.connect('clicked', self.gshell.menu_search)
        self.append_widget(self.search_button, "Search", "Search")

        self.append_widget(gtk.SeparatorToolItem(), None, None)

        self.zoom_in_button = gtk.ToolButton(gtk.STOCK_ZOOM_IN)
        self.zoom_in_button.set_label("Zoom In")
        self.zoom_in_button.set_sensitive(False)
        self.zoom_in_button.connect('clicked', self.gshell.menu_zoom_tab, 'zoom_in')
        self.append_widget(self.zoom_in_button, "Zoom In", "Zoom In")

        self.zoom_out_button = gtk.ToolButton(gtk.STOCK_ZOOM_OUT)
        self.zoom_out_button.set_label("Zoom Out")
        self.zoom_out_button.set_sensitive(False)
        self.zoom_out_button.connect('clicked', self.gshell.menu_zoom_tab, 'zoom_out')
        self.append_widget(self.zoom_out_button, "Zoom Out", "Zoom Out")

        self.zoom_orig_button = gtk.ToolButton(gtk.STOCK_ZOOM_100)
        self.zoom_orig_button.set_label("Zoom Default")
        self.zoom_orig_button.set_sensitive(False)
        self.zoom_orig_button.connect('clicked', self.gshell.menu_zoom_tab, 'zoom_orig')
        self.append_widget(self.zoom_orig_button, "Zoom Default", "Zoom Default")

        self.append_widget(gtk.SeparatorToolItem(), None, None)

        self.new_group_button = gtk.ToolButton(gtk.STOCK_DIRECTORY)
        self.new_group_button.set_label("New Tab Group")
        self.new_group_button.set_sensitive(False)
        self.new_group_button.connect('clicked', self.gshell.menuitem_response)
        self.append_widget(self.new_group_button, "New Tab Group", "New Tab Group")

        self.tab_arrange_button = gtk.ToolButton(gtk.STOCK_ZOOM_100)
        self.tab_arrange_button.set_label("Tab Arrange")
        self.tab_arrange_button.set_sensitive(False)
        self.tab_arrange_button.connect('clicked', self.gshell.menuitem_response)
        self.append_widget(self.tab_arrange_button, "Tab Arrange", "Tab Arrange")

        self.append_widget(gtk.SeparatorToolItem(), None, None)
