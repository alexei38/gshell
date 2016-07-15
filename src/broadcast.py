# -*- coding: utf-8 -*-

import gtk


class GshellBroadcastDialog(gtk.Dialog):

    def __init__(self, main_window, *args):
        gtk.Dialog.__init__(self, *args)
        self.config = main_window.config
        self.main_window = main_window
        self.build_dialog()
        self.run_window()

    def build_dialog(self):
        self.set_default_size(400, 500)
        self.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK)
        self.set_title("Enable Broadcast")
        
        self.store = gtk.ListStore(bool, str, str, int)
        self.tree = gtk.TreeView(self.store)

        renderer = gtk.CellRendererToggle()
        renderer.connect("toggled", self.on_cell_toggled)
        column = gtk.TreeViewColumn('Broadcast', renderer, active=0)
        column.set_sort_column_id(0)
        self.tree.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Terminal Name', renderer, text=1)
        column.set_sort_column_id(1)
        self.tree.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Host', renderer, text=2)
        column.set_sort_column_id(2)
        self.tree.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Page', renderer, text=3)
        column.set_visible(False)
        self.tree.append_column(column)

        scroll = gtk.ScrolledWindow()
        scroll.add(self.tree)

        self.vbox.pack_start(scroll, True, True, 0)

        terminals = self.main_window.notebook.get_all_terminals()
        for terminal in terminals:
            label = terminal.label.label.get_text().strip()
            host = None
            if terminal.host:
                host = terminal.host['host']
            page_num = self.main_window.notebook.get_page_by_terminal(terminal)
            self.store.append((terminal.broadcast, label, host, page_num))
        self.show_all()

    def run_window(self):
        response = self.run()
        if response == gtk.RESPONSE_OK:
            for row in self.store:
                broadcast = self.store.get_value(row.iter, 0)
                page_num = self.store.get_value(row.iter, 3)
                terminal = self.main_window.notebook.get_terminal_by_page(page_num)
                terminal.disable_broadcast()
                if broadcast:
                    terminal.enable_broadcast()
        self.destroy()

    def on_cell_toggled(self, widget, path):
        self.store[path][0] = not self.store[path][0]